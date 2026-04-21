"""
Unit tests voor scripts/run_monthly.py (maandelijkse batch-runner).

Testpatroon:
- _derive_periods() en _month_label_nl() worden direct getest (pure functies).
- main() wordt getest door subprocess.run te mocken en sys.argv te manipuleren.
  Aanroepargumenten worden geverifieerd — geen echte bestanden of DB vereist.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module laden via importlib (scripts/ is geen package)
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent.parent
_MODULE_PATH = _ROOT / "scripts" / "run_monthly.py"

_spec = importlib.util.spec_from_file_location("run_monthly", _MODULE_PATH)
assert _spec is not None, f"Kan module spec niet laden: {_MODULE_PATH}"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

# Aliassen voor leesbare tests
_derive_periods = _mod._derive_periods
_month_label_nl = _mod._month_label_nl
_run_script = _mod._run_script
_DEFAULT_PILLARS = _mod._DEFAULT_PILLARS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_subprocess_ok() -> MagicMock:
    """Retourneert een subprocess.CompletedProcess-mock met returncode 0."""
    m = MagicMock()
    m.returncode = 0
    return m


def _mock_subprocess_fail() -> MagicMock:
    """Retourneert een subprocess.CompletedProcess-mock met returncode 1."""
    m = MagicMock()
    m.returncode = 1
    return m


# ---------------------------------------------------------------------------
# 1. _derive_periods — pure functie, geen mocks nodig
# ---------------------------------------------------------------------------


class TestDerivePeriodsFunc:
    """Unit tests voor de _derive_periods hulpfunctie."""

    def test_huidig_jaar(self) -> None:
        assert _derive_periods("2026-03")["huidig_jaar"] == "2026"

    def test_vorig_jaar(self) -> None:
        assert _derive_periods("2026-03")["vorig_jaar"] == "2025"

    def test_matrix_from_is_jan(self) -> None:
        """matrix_from is altijd januari van het lopende jaar."""
        assert _derive_periods("2026-03")["matrix_from"] == "2026-01"

    def test_matrix_to_is_target(self) -> None:
        assert _derive_periods("2026-03")["matrix_to"] == "2026-03"

    def test_baseline_from(self) -> None:
        assert _derive_periods("2026-03")["baseline_from"] == "2025-01"

    def test_baseline_to(self) -> None:
        assert _derive_periods("2026-03")["baseline_to"] == "2025-12"

    def test_current_from_is_jan(self) -> None:
        assert _derive_periods("2026-03")["current_from"] == "2026-01"

    def test_current_to_is_target(self) -> None:
        assert _derive_periods("2026-03")["current_to"] == "2026-03"

    def test_jaarsgrens_januari(self) -> None:
        """Jaarovergang: doelmaand januari 2026 → baseline 2025."""
        p = _derive_periods("2026-01")
        assert p["vorig_jaar"] == "2025"
        assert p["baseline_from"] == "2025-01"
        assert p["baseline_to"] == "2025-12"
        assert p["current_from"] == "2026-01"
        assert p["current_to"] == "2026-01"

    def test_jaar_2027(self) -> None:
        """Periodelogica klopt ook voor toekomstige jaren."""
        p = _derive_periods("2027-06")
        assert p["huidig_jaar"] == "2027"
        assert p["vorig_jaar"] == "2026"
        assert p["baseline_from"] == "2026-01"
        assert p["baseline_to"] == "2026-12"


# ---------------------------------------------------------------------------
# 2. _month_label_nl — pure functie
# ---------------------------------------------------------------------------


class TestMonthLabelNl:
    """Unit tests voor de _month_label_nl hulpfunctie."""

    def test_maart(self) -> None:
        assert _month_label_nl("2026-03") == "maart 2026"

    def test_januari(self) -> None:
        assert _month_label_nl("2026-01") == "januari 2026"

    def test_december(self) -> None:
        assert _month_label_nl("2025-12") == "december 2025"

    def test_bevat_jaar(self) -> None:
        label = _month_label_nl("2026-07")
        assert "2026" in label

    def test_bevat_maandnaam(self) -> None:
        label = _month_label_nl("2026-07")
        assert "juli" in label.lower()


# ---------------------------------------------------------------------------
# 3. main() — subprocess.run gemockt, sys.argv gemanipuleerd
# ---------------------------------------------------------------------------


class TestMainMatrixStap:
    """Verifieer dat de matrix-stap correct wordt aangeroepen."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Patcht OUTPUT_PATH naar tmp_path — voorkomt echte mapAanmaak in output/."""
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_generate_matrix_wordt_aangeroepen(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """main() roept generate_matrix.py aan."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        calls = [str(c) for c in mock_run.call_args_list]
        assert any("generate_matrix.py" in c for c in calls)

    def test_matrix_from_periode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--from wordt ingesteld op januari van het doeljaar."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        idx = matrix_args.index("--from")
        assert matrix_args[idx + 1] == "2026-01"

    def test_matrix_to_periode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--to wordt ingesteld op de doelmaand."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        idx = matrix_args.index("--to")
        assert matrix_args[idx + 1] == "2026-03"

    def test_matrix_volgt_pillar_arg(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Matrix gebruikt de opgegeven --pillar argumenten (niet hardcoded pharma)."""
        monkeypatch.setattr(
            sys, "argv", ["run_monthly.py", "--month", "2026-03", "--pillar", "care"]
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        # Eerste subprocess-call = matrix voor 'care'
        matrix_args = mock_run.call_args_list[0][0][0]
        idx = matrix_args.index("--pillar")
        assert matrix_args[idx + 1] == "care"

    def test_matrix_lang_both(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Matrix gebruikt altijd --lang both."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        assert "--lang" in matrix_args
        idx = matrix_args.index("--lang")
        assert matrix_args[idx + 1] == "both"

    def test_matrix_krijgt_output_arg(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Matrix-stap krijgt --output doorgegeven (OUTPUT_PATH rechtstreeks)."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        assert "--output" in matrix_args
        idx = matrix_args.index("--output")
        output_pad = Path(matrix_args[idx + 1])
        assert output_pad == tmp_path


class TestMainEvolutieStap:
    """Verifieer dat de evolutiestap correct wordt aangeroepen."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_generate_all_evolutions_wordt_aangeroepen(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() roept generate_all_evolutions.py aan."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        calls = [str(c) for c in mock_run.call_args_list]
        assert any("generate_all_evolutions.py" in c for c in calls)

    def test_evolutie_baseline_van(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Baseline start op 2025-01 bij doelmaand 2026-03."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        idx = evo_args.index("--baseline")
        assert evo_args[idx + 1] == "2025-01"

    def test_evolutie_baseline_tot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Baseline eindigt op 2025-12 bij doelmaand 2026-03."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        idx = evo_args.index("--baseline")
        assert evo_args[idx + 2] == "2025-12"

    def test_evolutie_current_van(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Current start op 2026-01 bij doelmaand 2026-03."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        idx = evo_args.index("--current")
        assert evo_args[idx + 1] == "2026-01"

    def test_evolutie_current_tot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Current eindigt op de doelmaand."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        idx = evo_args.index("--current")
        assert evo_args[idx + 2] == "2026-03"

    def test_evolutie_year_arg(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--year wordt meegegeven als het doeljaar."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--year" in evo_args
        idx = evo_args.index("--year")
        assert evo_args[idx + 1] == "2026"

    def test_evolutie_standaard_alle_pijlers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Zonder --pillar worden alle 5 standaard pijlers doorgegeven."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--pillar" in evo_args
        idx = evo_args.index("--pillar")
        pijlers_in_call = evo_args[idx + 1 :]
        for pijler in _DEFAULT_PILLARS:
            assert pijler in pijlers_in_call

    def test_evolutie_specifieke_pijlers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Opgegeven pijlers worden doorgegeven aan generate_all_evolutions.py."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["run_monthly.py", "--month", "2026-03", "--pillar", "pharma", "care"],
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        idx = evo_args.index("--pillar")
        pijlers_in_call = evo_args[idx + 1 :]
        assert "pharma" in pijlers_in_call
        assert "care" in pijlers_in_call
        assert "zorgi" not in pijlers_in_call

    def test_evolutie_krijgt_output_arg(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Evolutiestap krijgt --output doorgegeven (OUTPUT_PATH rechtstreeks)."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        # Laatste call = evolutie (na n_pillar matrix-calls)
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--output" in evo_args
        idx = evo_args.index("--output")
        output_pad = Path(evo_args[idx + 1])
        assert output_pad == tmp_path


# ---------------------------------------------------------------------------
# 4. Output pad — beide scripts krijgen OUTPUT_PATH rechtstreeks
# ---------------------------------------------------------------------------


class TestGedateerdeSubmap:
    """Verifieer dat beide sub-scripts een gedateerde submap van OUTPUT_PATH ontvangen."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_beide_scripts_zelfde_output_pad(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Matrix en evolutie ontvangen exact hetzelfde --output pad (OUTPUT_PATH)."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        evo_args = mock_run.call_args_list[-1][0][0]
        matrix_out = matrix_args[matrix_args.index("--output") + 1]
        evo_out = evo_args[evo_args.index("--output") + 1]
        assert matrix_out == evo_out

    def test_output_pad_is_output_root(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Output gaat naar OUTPUT_PATH rechtstreeks — de sub-scripts maken de dated submap."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        output_pad = Path(matrix_args[matrix_args.index("--output") + 1])
        assert output_pad == tmp_path

    def test_output_submap_naam_bevat_datum(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """OUTPUT_PATH wordt ongewijzigd doorgegeven (sub-scripts maken zelf dated submap)."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        output_pad = Path(matrix_args[matrix_args.index("--output") + 1])
        assert output_pad == tmp_path

    def test_output_submap_wordt_aangemaakt(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """OUTPUT_PATH bestaat na de run."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        assert tmp_path.exists()
        assert tmp_path.is_dir()


# ---------------------------------------------------------------------------
# 5. Vlaggen: --chart, --no-charts, --force-csv
# ---------------------------------------------------------------------------


class TestVlaggen:
    """Tests voor de --no-charts en --force-csv vlaggen."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_chart_flag_standaard_aan(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--chart wordt standaard meegegeven aan generate_all_evolutions.py."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--chart" in evo_args

    def test_no_charts_slaat_chart_over(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--no-charts zorgt dat --chart NIET doorgegeven wordt."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03", "--no-charts"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--chart" not in evo_args

    def test_force_csv_doorgegeven_aan_evolutie(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--force-csv wordt doorgegeven aan generate_all_evolutions.py."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03", "--force-csv"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--force-csv" in evo_args

    def test_force_csv_niet_aan_matrix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--force-csv wordt NIET doorgegeven aan generate_matrix.py."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03", "--force-csv"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        matrix_args = mock_run.call_args_list[0][0][0]
        assert "--force-csv" not in matrix_args

    def test_no_charts_en_force_csv_combinatie(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """--no-charts en --force-csv kunnen gecombineerd worden."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["run_monthly.py", "--month", "2026-03", "--no-charts", "--force-csv"],
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        evo_args = mock_run.call_args_list[-1][0][0]
        assert "--chart" not in evo_args
        assert "--force-csv" in evo_args


# ---------------------------------------------------------------------------
# 6. Foutafhandeling — exit bij mislukt subprocess
# ---------------------------------------------------------------------------


class TestFoutafhandeling:
    """Tests voor sys.exit bij falende subprocess-aanroepen."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_exit_bij_matrix_fout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """sys.exit wordt aangeroepen als generate_matrix.py faalt."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_fail()
            with pytest.raises(SystemExit) as exc_info:
                _mod.main()
        assert exc_info.value.code == 1

    def test_exit_bij_evolutie_fout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """sys.exit wordt aangeroepen als generate_all_evolutions.py faalt."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            # Alle matrix-calls OK, evolutie faalt
            ok_calls = [_mock_subprocess_ok() for _ in range(len(_DEFAULT_PILLARS))]
            mock_run.side_effect = [*ok_calls, _mock_subprocess_fail()]
            with pytest.raises(SystemExit) as exc_info:
                _mod.main()
        assert exc_info.value.code == 1

    def test_evolutie_niet_aangeroepen_bij_matrix_fout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Als matrix faalt, wordt generate_all_evolutions.py niet meer aangeroepen."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_fail()
            with pytest.raises(SystemExit):
                _mod.main()
        assert mock_run.call_count == 1


# ---------------------------------------------------------------------------
# 7. Aanroepvolgorde
# ---------------------------------------------------------------------------


class TestAanroepvolgorde:
    """Verifieer dat matrix vóór evolutie wordt uitgevoerd."""

    @pytest.fixture(autouse=True)
    def _patch_output_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(_mod, "OUTPUT_PATH", tmp_path)

    def test_matrix_eerst_dan_evolutie(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Eerste subprocess-aanroepen zijn matrix (per pijler), laatste is evolutie."""
        monkeypatch.setattr(sys, "argv", ["run_monthly.py", "--month", "2026-03"])
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_subprocess_ok()
            _mod.main()
        # N_DEFAULT_PILLARS matrix-calls + 1 evolutie-call
        assert mock_run.call_count == len(_DEFAULT_PILLARS) + 1
        first_args = mock_run.call_args_list[0][0][0]
        last_args = mock_run.call_args_list[-1][0][0]
        assert "generate_matrix.py" in first_args[1]
        assert "generate_all_evolutions.py" in last_args[1]
