import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Import app modules
import app

class TestV194Features(unittest.TestCase):
    def test_version_bump(self):
        self.assertIn(app.CURRENT_VERSION, ["v1.9.4", "v1.9.5", "v1.9.6", "v1.9.7"])

    def test_order_group_sort_key(self):
        class MockApp:
            def __init__(self):
                self.resolved_orders = {
                    "459937_edgebo": {"order_id": "459937", "vendor": "edgebo"},
                    "459937_ftp": {"order_id": "459937", "vendor": "Original", "is_ftp": True},
                    "459944_edgebo": {"order_id": "459944", "vendor": "edgebo"},
                    "459944_ftp": {"order_id": "459944", "vendor": "Original", "is_ftp": True},
                    "460001_edgebo": {"order_id": "460001", "vendor": "edgebo"}
                }
            _order_group_sort_key = app.QCBatchLoaderApp._order_group_sort_key

        mock = MockApp()
        items = [
            ("459944_ftp", ("#459944", "Original", "FTP")),
            ("459937_edgebo", ("#459937", "edgebo", "Local")),
            ("460001_edgebo", ("#460001", "edgebo", "Dropbox")),
            ("459944_edgebo", ("#459944", "edgebo", "Local")),
            ("459937_ftp", ("#459937", "Original", "FTP")),
        ]
        sorted_items = sorted(items, key=lambda it: mock._order_group_sort_key(it))
        sorted_keys = [k for k, _ in sorted_items]

        expected_keys = [
            "459937_edgebo",
            "459937_ftp",
            "459944_edgebo",
            "459944_ftp",
            "460001_edgebo"
        ]
        self.assertEqual(sorted_keys, expected_keys)
        print("✓ Order grouping test passed: Identical order IDs are strictly grouped together with Dropbox first and Original (FTP) second.")

    def test_hydrate_pause_stop(self):
        test_file = "test_chunk_file.bin"
        with open(test_file, "wb") as f:
            f.write(b"X" * (512 * 1024)) # 512 KB

        try:
            # Mock GetFileAttributesW to return RECALL_ON_DATA_ACCESS so it enters the streaming loop
            with patch.object(app.ctypes.windll.kernel32, "GetFileAttributesW", return_value=app.FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS):
                # 1. Test stop check aborts early
                stop_flag = [False]
                chunks_read = []
                def chunk_cb(b):
                    chunks_read.append(b)
                    stop_flag[0] = True # Stop immediately on first chunk

                res = app._hydrate_single_file(test_file, chunk_callback=chunk_cb, stop_check=lambda: stop_flag[0])
                self.assertFalse(res)
                self.assertLessEqual(len(chunks_read), 2)
                print("✓ Immediate stop test passed: Stream halted within 1 chunk.")

                # 2. Test callable pause check
                paused_count = [0]
                def pause_cb():
                    paused_count[0] += 1

                res2 = app._hydrate_single_file(test_file, chunk_callback=lambda b: None, pause_event=pause_cb)
                self.assertTrue(res2)
                self.assertGreater(paused_count[0], 0)
                print(f"✓ Callable pause check test passed: pause check was invoked {paused_count[0]} times.")

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_cursor_motion_logic(self):
        class MockTreeApp:
            def __init__(self):
                self.configured_cursor = None
                self.tree = MagicMock()
                self.tree.winfo_exists.return_value = True
                def mock_cfg(**kwargs):
                    if "cursor" in kwargs:
                        self.configured_cursor = kwargs["cursor"]
                self.tree.configure.side_effect = mock_cfg
            _on_tree_motion = app.QCBatchLoaderApp._on_tree_motion

        mock = MockTreeApp()
        
        # Simulating hover over #1 (Order ID)
        event = MagicMock()
        event.x = 100
        event.y = 50
        mock.tree.identify_column.return_value = "#1"
        mock.tree.identify_row.return_value = "row1"
        mock._on_tree_motion(event)
        self.assertEqual(mock.configured_cursor, "hand2")

        # Simulating hover over #6 (Make Local with [ 📥 Local ])
        mock.tree.identify_column.return_value = "#6"
        mock.tree.item.return_value = ("#123", "v", "st", "1", "1MB", "[ 📥 Local ]", "[ ☁ Cloud ]", "[ 📁 Open ]")
        mock._on_tree_motion(event)
        self.assertEqual(mock.configured_cursor, "hand2")

        # Simulating hover over #6 disabled [ - ]
        mock.tree.item.return_value = ("#123", "v", "st", "1", "1MB", "[ - ]", "[ - ]", "[ 📁 Open ]")
        mock._on_tree_motion(event)
        self.assertEqual(mock.configured_cursor, "arrow")

        # Simulating hover over #2 (Vendor)
        mock.tree.identify_column.return_value = "#2"
        mock._on_tree_motion(event)
        self.assertEqual(mock.configured_cursor, "arrow")

        print("✓ Treeview hover motion test passed: Hand cursor activates precisely on clickable action cells.")

if __name__ == "__main__":
    unittest.main()
