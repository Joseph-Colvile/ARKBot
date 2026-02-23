import unittest

from bot.main import _format_status
from bot.nitrado import ServerStatus


class BotFormattingTests(unittest.TestCase):
    def test_format_status_with_player_counts(self):
        status = ServerStatus(
            state="started",
            query_status="online",
            player_current=2,
            player_max=12,
            game_human="ARK: Survival Ascended",
        )

        message = _format_status(status)

        self.assertIn("ARK: Survival Ascended", message)
        self.assertIn("State: **started**", message)
        self.assertIn("Query: `online`", message)
        self.assertIn("Players: `2/12`", message)

    def test_format_status_without_player_counts(self):
        status = ServerStatus(
            state="stopped",
            query_status=None,
            player_current=None,
            player_max=None,
            game_human=None,
        )

        message = _format_status(status)

        self.assertIn("**ARK**", message)
        self.assertIn("Query: `unknown`", message)
        self.assertIn("Players: `Unknown`", message)


if __name__ == "__main__":
    unittest.main()
