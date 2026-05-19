import io
from datetime import datetime
import unittest
from pathlib import Path


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    started_at = datetime.now()
    output = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(base_dir), pattern="*_tests.py")
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    finished_at = datetime.now()
    status = "PASS" if result.wasSuccessful() else "FAIL"
    report_path = reports_dir / f"python_app_tests_{finished_at.strftime('%Y%m%d_%H%M%S')}.md"

    lines = [
        "# Relatorio de Testes Python - OficinaPro",
        "",
        f"- Status: {status}",
        f"- Inicio: {started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Fim: {finished_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Duracao: {(finished_at - started_at).total_seconds():.2f}s",
        f"- Testes executados: {result.testsRun}",
        f"- Falhas: {len(result.failures)}",
        f"- Erros: {len(result.errors)}",
        "",
        "## Saida detalhada",
        "",
        "```text",
        output.getvalue().strip(),
        "```",
    ]
    if result.failures:
        lines.extend(["", "## Falhas", ""])
        for test, traceback in result.failures:
            lines.extend([f"### {test}", "", "```text", traceback.strip(), "```"])
    if result.errors:
        lines.extend(["", "## Erros", ""])
        for test, traceback in result.errors:
            lines.extend([f"### {test}", "", "```text", traceback.strip(), "```"])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(output.getvalue(), end="")
    print(f"\nRelatorio gerado: {report_path}")
    raise SystemExit(0 if result.wasSuccessful() else 1)
