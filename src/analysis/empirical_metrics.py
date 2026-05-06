from src.analysis.selenium_metrics_loader import (
    SUMMARY_FILE,
    process_selenium_metrics,
)


def main() -> None:
    summary, _ = process_selenium_metrics()
    print(f"Resumo salvo em: {SUMMARY_FILE}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
