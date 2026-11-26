import unittest
from unittest.mock import MagicMock
import app


class TestV196Features(unittest.TestCase):
    def test_version_bump(self):
        self.assertEqual(app.CURRENT_VERSION, "v1.9.6")

    def test_theme_lavender_palette(self):
        light = app.BRAND_THEMES["light"]
        self.assertEqual(light["tree_select"], "#9B93EE")
        for key in ("status_local_bg", "status_sync_bg", "status_cloud_bg", "status_notfound_bg", "status_ftp_bg"):
            self.assertEqual(light[key], "#C3BEF4")

    def test_multi_vendor_row_color_tags(self):
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
                self.resolved_orders = {
                    k: {"order_id": k.split("_")[0], "vendor": v[1]} for k, v in self.items.items()
                }
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
        self.assertEqual(m.applied_tags["460040_path_subs"], ("row_v2",))
        self.assertEqual(m.applied_tags["460043_creative_path"], ("row_local",))

    def test_cursor_motion_original_and_completed_columns(self):
        class MockTreeApp:
            def __init__(self):
                self.configured_cursor = None
                self.tree = MagicMock()
                self.tree.winfo_exists.return_value = True
                self.tree.configure.side_effect = lambda **kw: setattr(self, "configured_cursor", kw.get("cursor", self.configured_cursor))
            _on_tree_motion = app.QCBatchLoaderApp._on_tree_motion

        m = MockTreeApp()
        ev = MagicMock(x=100, y=50)
        m.tree.identify_row.return_value = "r1"
        m.tree.item.return_value = ("#460040", "creative_path", "Dropbox", "0/1", "12 MB", "Local", "Cloud", "📁 Open", "-")

        # #8 Original has "📁 Open" -> hand2
        m.tree.identify_column.return_value = "#8"
        m._on_tree_motion(ev)
        self.assertEqual(m.configured_cursor, "hand2")

        # #9 Completed has "-" -> arrow
        m.tree.identify_column.return_value = "#9"
        m._on_tree_motion(ev)
        self.assertEqual(m.configured_cursor, "arrow")


if __name__ == "__main__":
    unittest.main()
