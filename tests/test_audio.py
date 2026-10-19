import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QCheckBox

from shet_shet.audio import Mp3CuePlayer
from shet_shet.ui import MainWindow


class Mp3CuePlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_genuine_on_to_off_transitions_request_one_cue_each(self):
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        audio_player = SimpleNamespace(play=Mock())
        settings = SimpleNamespace(setValue=Mock())
        worker = SimpleNamespace(
            isRunning=lambda: True,
            set_options=Mock(),
            stop=Mock(),
        )
        window = SimpleNamespace(
            audio_player=audio_player,
            settings=settings,
            effect_check=checkbox,
            mirror_check=SimpleNamespace(isChecked=lambda: True),
            filter_style_combo=SimpleNamespace(currentData=lambda: "dots"),
            color_combo=SimpleNamespace(currentData=lambda: "#68F7D5"),
            thickness_slider=SimpleNamespace(value=lambda: 3),
            smoothing_slider=SimpleNamespace(value=lambda: 55),
            worker=worker,
        )
        window._options = lambda: MainWindow._options(window)
        window._push_options = lambda: MainWindow._push_options(window)
        checkbox.toggled.connect(lambda enabled: MainWindow._on_effect_toggled(window, enabled))

        checkbox.setChecked(False)
        checkbox.setChecked(False)
        checkbox.setChecked(True)
        checkbox.setChecked(True)
        checkbox.setChecked(False)

        self.assertEqual(audio_player.play.call_count, 2)
        self.assertEqual(worker.set_options.call_count, 3)
        worker.stop.assert_not_called()
        self.assertFalse(worker.set_options.call_args.args[0]["effect"])

    def test_saved_off_state_does_not_play_during_window_initialization(self):
        class FakeSettings:
            def __init__(self, *_args):
                self.values = {"effect": False, "mirror": True}

            def value(self, key, default=None, type=None):
                value = self.values.get(key, default)
                return type(value) if type is not None else value

            def setValue(self, key, value):
                self.values[key] = value

        with patch("shet_shet.ui.QSettings", FakeSettings):
            window = MainWindow(Path(__file__).resolve().parent.parent)
        self.assertFalse(window.effect_check.isChecked())
        self.assertIsNone(window.audio_player._thread)
        window.close()

    def test_missing_mp3_logs_and_returns_without_starting_audio_worker(self):
        path = Path(__file__).resolve().parent / "missing-filter-cue.mp3"
        player = Mp3CuePlayer(path)
        with self.assertLogs("shet_shet.audio", level="WARNING"):
            self.assertFalse(player.play())
        self.assertIsNone(player._thread)
        player.close()

    def test_audio_requests_are_reused_and_shutdown_closes_session(self):
        asset = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "audio"
            / "shet-shet-nakita-ko-akosidogie-meme-oicwbjyekq0_Jd8GzV3n.mp3"
        )
        self.assertTrue(asset.is_file())
        played = []
        playback_threads = []
        condition = threading.Condition()
        sessions = []

        class FakeSession:
            def __init__(self, path):
                self.path = path
                self.open_count = 0
                self.stop_count = 0
                self.close_count = 0
                sessions.append(self)

            def open(self):
                self.open_count += 1

            def stop(self):
                self.stop_count += 1

            def play(self):
                with condition:
                    played.append(self.path)
                    playback_threads.append(threading.get_ident())
                    condition.notify_all()

            def close(self):
                self.close_count += 1

        player = Mp3CuePlayer(asset, session_factory=FakeSession)
        self.assertTrue(player.play())
        with condition:
            self.assertTrue(condition.wait_for(lambda: len(played) == 1, timeout=2))
        self.assertTrue(player.play())
        with condition:
            self.assertTrue(condition.wait_for(lambda: len(played) == 2, timeout=2))
        player.close()

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].open_count, 1)
        self.assertEqual(sessions[0].stop_count, 1)
        self.assertEqual(sessions[0].close_count, 1)
        self.assertTrue(playback_threads)
        self.assertTrue(all(thread_id != threading.get_ident() for thread_id in playback_threads))
        self.assertFalse(player.play())


if __name__ == "__main__":
    unittest.main()
