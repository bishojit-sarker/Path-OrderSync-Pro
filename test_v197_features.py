import threading
import unittest
from unittest.mock import MagicMock
import app


class TestV197Features(unittest.TestCase):
    def test_version_bump(self):
        self.assertEqual(app.CURRENT_VERSION, "v1.9.8")

    def test_palette_and_font_colors(self):
        light = app.BRAND_THEMES["light"]
        self.assertEqual(light["tree_select"], "#9B93EE")
        self.assertEqual(light["tree_select_fg"], "#1F1D2F")
        for key in ("status_local_bg", "status_sync_bg", "status_cloud_bg", "status_notfound_bg", "status_ftp_bg"):
            self.assertEqual(light[key], "#D7D3F8")
        for key in ("status_local_fg", "status_sync_fg", "status_cloud_fg", "status_notfound_fg", "status_ftp_fg"):
            self.assertEqual(light[key], "#1F1D2F")

    def test_multi_vendor_two_tone_tags(self):
        class MockApp:
            def __init__(self):
                self.applied_tags = {}
                self.tree = MagicMock()
                self.tree.winfo_exists.return_value = True
                self.items = {
                    "460040_creative_path": ("#460040", "creative_path", "Dropbox", "0/1", "12 MB", "Local", "Cloud", "📁 Open", "📁 Open"),
                    "460040_khandoker": ("#460040", "khandoker", "Dropbox", "0/1", "56 MB", "Local", "Cloud", "📁 Open", "📁 Open"),
                    "460040_path_subs": ("#460040", "path_subs", "Dropbox", "0/1", "37 MB", "Local", "Cloud", "📁 Open", "📁 Open"),
                    "460043_creative_path": ("#460043", "creative_path", "Local", "3/3", "149 MB", "Local", "Cloud", "📁 Open", "📁 Open"),
                }
                self.resolved_orders = {k: {"order_id": k.split("_")[0], "vendor": v[1]} for k, v in self.items.items()}
                self.tree.get_children.return_value = list(self.items.keys())
                def mock_item(iid, *args, **kwargs):
                    if "tags" in kwargs:
                        self.applied_tags[iid] = kwargs["tags"]
                    return self.items[iid]
                self.tree.item.side_effect = mock_item
            _get_clean_order_id = app.QCBatchLoaderApp._get_clean_order_id
            _apply_row_color_tags = app.QCBatchLoaderApp._apply_row_color_tags

        m = MockApp()
        m._apply_row_color_tags()
        self.assertEqual(m.applied_tags["460040_creative_path"], ("row_v0",))
        self.assertEqual(m.applied_tags["460040_khandoker"], ("row_v1",))
        self.assertEqual(m.applied_tags["460040_path_subs"], ("row_v1",))
        self.assertEqual(m.applied_tags["460043_creative_path"], ("row_local",))

    def test_global_and_selective_pause_resume_stop(self):
        class MockSyncApp:
            def __init__(self):
                self.is_running = True
                self.is_paused = False
                self.stop_requested = False
                self.pause_event = threading.Event()
                self.pause_event.set()
                self.paused_order_ids = set()
                self.stopped_order_ids = set()
                self.order_checkboxes = {}
                self._selected_order_ids = []
                self.accent_orange = "#f6ce4c"
                self.accent_green = "#10b981"
                self.btn_pause = MagicMock()
                self.btn_stop = MagicMock()
                self.speed_eta_lbl = MagicMock()
                self.status_var = MagicMock()
                self.resolved_orders = {
                    "460040_creative_path": {"order_id": "460040", "vendor": "creative_path"},
                    "460043_creative_path": {"order_id": "460043", "vendor": "creative_path"},
                }
                self.rows = {
                    "460040_creative_path": ["#460040", "creative_path", "Syncing 20.0%", "1/5", "10 MB", "⏳ Syncing", "Cloud", "-", "📁 Open"],
                    "460043_creative_path": ["#460043", "creative_path", "Syncing 40.0%", "2/5", "20 MB", "⏳ Syncing", "Cloud", "-", "📁 Open"],
                }
                self.selected = []
                self.tree = MagicMock()
                self.tree.exists.side_effect = lambda iid: iid in self.rows
                self.tree.get_children.side_effect = lambda: list(self.rows.keys())
                self.tree.selection.side_effect = lambda: list(self.selected)
                def mock_item(iid, *args, **kwargs):
                    if "values" in kwargs:
                        self.rows[iid] = list(kwargs["values"])
                    return tuple(self.rows[iid])
                self.tree.item.side_effect = mock_item
            _get_clean_order_id = app.QCBatchLoaderApp._get_clean_order_id
            _toggle_pause = app.QCBatchLoaderApp._toggle_pause
            _request_stop = app.QCBatchLoaderApp._request_stop

        m = MockSyncApp()

        # 1. Global Pause -> button becomes Resume, pause_event cleared
        m._toggle_pause()
        self.assertTrue(m.is_paused)
        self.assertFalse(m.pause_event.is_set())
        m.btn_pause.configure.assert_with = m.btn_pause.configure.call_args
        self.assertEqual(m.btn_pause.configure.call_args.kwargs["text"], "▶ Resume")

        # 2. Global Resume -> button becomes Pause, pause_event set
        m._toggle_pause()
        self.assertFalse(m.is_paused)
        self.assertTrue(m.pause_event.is_set())
        self.assertEqual(m.btn_pause.configure.call_args.kwargs["text"], "⏸ Pause")

        # 3. Selective Pause on single order 460040 -> only 460040 paused, button becomes Resume
        m.selected = ["460040_creative_path"]
        m._toggle_pause()
        self.assertEqual(m.paused_order_ids, {"460040"})
        self.assertEqual(m.rows["460040_creative_path"][2], "⏸ Paused")
        self.assertEqual(m.rows["460043_creative_path"][2], "Syncing 40.0%")
        self.assertEqual(m.btn_pause.configure.call_args.kwargs["text"], "▶ Resume")

        # 4. Selective Resume on single order 460040 -> 460040 resumed, button becomes Pause
        m._toggle_pause()
        self.assertEqual(m.paused_order_ids, set())
        self.assertEqual(m.rows["460040_creative_path"][2], "Syncing...")
        self.assertEqual(m.btn_pause.configure.call_args.kwargs["text"], "⏸ Pause")

        # 5. Selective Stop on single order 460040 -> only 460040 stopped, global stop_requested remains False
        m._request_stop()
        self.assertEqual(m.stopped_order_ids, {"460040"})
        self.assertFalse(m.stop_requested)
        self.assertEqual(m.rows["460040_creative_path"][2], "⏹ Stopped")
        self.assertEqual(m.rows["460043_creative_path"][2], "Syncing 40.0%")

        # 6. Global Stop -> stop_requested becomes True
        m.selected = []
        m._request_stop()
        self.assertTrue(m.stop_requested)


if __name__ == "__main__":
    unittest.main()
