from jarvis_cmd.brain import plan_command
from jarvis_cmd.executor import run_command
from jarvis_cmd.memory import append_history
from jarvis_cmd.safety import check_command
from jarvis_cmd.telegram_notifier import TelegramNotifier, format_event
from jarvis_cmd.logger import get_logger
from jarvis_cmd.colors import success, error, warning, info, command, dim
from jarvis_cmd.actions import get_actions
from jarvis_cmd.conversation import get_conversation


def _confirm() -> bool:
    answer = input("Подтвердить выполнение? [y/N]: ").strip().lower()
    return answer in {"y", "yes", "д", "да"}


def main() -> None:
    logger = get_logger()
    logger.info("Jarvis Command Core started")

    notifier = TelegramNotifier()
    conversation = get_conversation("cli")

    print(success("Jarvis Command Core", bold=True))
    print(dim("Напиши задачу. Выход: exit"))
    if notifier.enabled:
        notifier.send(format_event("Сессия запущена"))
        logger.info("Telegram notifications enabled")
    while True:
        try:
            user_text = input(f"\n{info('Ты:', bold=True)} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{info('Jarvis:')} До связи.")
            logger.info("Session ended by user interrupt")
            if notifier.enabled:
                notifier.send(format_event("Сессия завершена"))
            break

        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit", "выход"}:
            print(f"{info('Jarvis:')} До связи.")
            logger.info("Session ended normally")
            if notifier.enabled:
                notifier.send(format_event("Сессия завершена"))
            break

        try:
            # Get conversation history for context
            history = conversation.get_messages()
            plan = plan_command(user_text, conversation_history=history)
            logger.debug(f"Plan: intent={plan.intent}, command={plan.command}, source={plan.source}")
        except Exception as exc:
            print(error(f"Jarvis: Ошибка планирования: {exc}"))
            logger.error(f"Planning error: {exc}", exc_info=True)
            continue

        # Handle chat intent
        if plan.intent == "chat":
            print(f"{info('Jarvis:')} {plan.reason}")
            logger.info(f"Chat: {plan.reason}")

            # Save to conversation history
            conversation.add_message("user", user_text)
            conversation.add_message("assistant", plan.reason)

            append_history(
                {
                    "user": user_text,
                    "plan_source": plan.source,
                    "intent": "chat",
                    "message": plan.reason,
                }
            )
            continue

        # Handle special intents (search, calendar, weather, etc)
        if plan.intent in {"search", "calendar", "weather", "reminder", "time"}:
            print(f"{info('Jarvis:')} {plan.reason}")

            try:
                actions = get_actions()
                params = plan.params or {}

                if plan.intent == "search":
                    result = actions.search_internet(params.get("query", user_text))
                elif plan.intent == "calendar":
                    result = actions.add_calendar_event(
                        title=params.get("title", "Событие"),
                        when=params.get("when", "сегодня"),
                        description=params.get("description", "")
                    )
                elif plan.intent == "weather":
                    result = actions.get_weather_info(params.get("city", "Moscow"))
                elif plan.intent == "reminder":
                    result = actions.set_reminder(
                        text=params.get("text", "Напоминание"),
                        when=params.get("when", "через час")
                    )
                elif plan.intent == "time":
                    result = actions.get_time_info()

                print(f"\n{result.message}")
                logger.info(f"Action {plan.intent} completed: {result.success}")

                append_history({
                    "user": user_text,
                    "plan_source": plan.source,
                    "intent": plan.intent,
                    "success": result.success,
                    "message": result.message[:500],
                })

            except Exception as exc:
                print(error(f"\n❌ Ошибка выполнения действия: {exc}"))
                logger.error(f"Action error: {exc}", exc_info=True)

            continue

        if plan.intent == "answer" or not plan.command:
            print(f"{info('Jarvis:')} {plan.reason}")
            logger.info(f"Answer: {plan.reason}")
            append_history(
                {
                    "user": user_text,
                    "plan_source": plan.source,
                    "intent": "answer",
                    "message": plan.reason,
                }
            )
            continue

        decision = check_command(plan.command)
        print(f"{info('Jarvis:')} {plan.reason}")
        print(f"{command('Команда:')} {plan.command}")

        if not decision.allowed:
            print(error(f"⛔ Безопасность: {decision.reason}"))
        elif decision.requires_confirmation:
            print(warning(f"⚠️  Безопасность: {decision.reason}"))
        else:
            print(success(f"✓ Безопасность: {decision.reason}"))

        if not decision.allowed:
            logger.warning(f"Command blocked: {plan.command}")
            if notifier.enabled:
                notifier.send(
                    format_event(
                        "Команда заблокирована",
                        f"Запрос: {user_text}\nКоманда: {plan.command}",
                    )
                )
            append_history(
                {
                    "user": user_text,
                    "plan_source": plan.source,
                    "intent": "execute",
                    "command": plan.command,
                    "blocked": True,
                    "reason": decision.reason,
                }
            )
            continue

        if decision.requires_confirmation and not _confirm():
            print(warning("Jarvis: Отменено."))
            logger.info(f"Command cancelled by user: {plan.command}")
            if notifier.enabled:
                notifier.send(format_event("Рискованная команда отменена", f"Команда: {plan.command}"))
            append_history(
                {
                    "user": user_text,
                    "plan_source": plan.source,
                    "intent": "execute",
                    "command": plan.command,
                    "confirmed": False,
                }
            )
            continue

        try:
            result = run_command(plan.command)
            logger.info(f"Command executed: {plan.command}, exit_code={result.exit_code}")
        except Exception as exc:
            print(error(f"\n❌ Ошибка выполнения: {exc}"))
            logger.error(f"Execution error: {exc}", exc_info=True)
            continue

        if result.stdout:
            print(f"\n{dim('STDOUT:')}\n{result.stdout}")
        if result.stderr:
            print(f"\n{warning('STDERR:')}\n{result.stderr}")

        if result.exit_code == 0:
            print(f"\n{success(f'✓ Exit code: {result.exit_code}')}")
        else:
            print(f"\n{error(f'✗ Exit code: {result.exit_code}')}")

        if notifier.enabled:
            status = "успешно" if result.exit_code == 0 else "с ошибкой"
            body = f"Команда: {plan.command}\nКод: {result.exit_code}\nСтатус: {status}"
            notifier.send(format_event("Команда выполнена", body))

        append_history(
            {
                "user": user_text,
                "plan_source": plan.source,
                "intent": "execute",
                "command": plan.command,
                "exit_code": result.exit_code,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:2000],
            }
        )


if __name__ == "__main__":
    main()
