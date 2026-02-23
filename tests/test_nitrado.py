import unittest

from bot.nitrado import NitradoApiError, NitradoClient


class NitradoClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_status_parses_payload(self):
        client = NitradoClient(token="x", service_id="123")

        async def fake_get_json(_):
            return {
                "data": {
                    "gameserver": {
                        "status": "started",
                        "settings": {"config": {"game_human": "ARK: Survival Evolved"}},
                        "query": {
                            "status": "online",
                            "player_current": 3,
                            "player_max": 10,
                        },
                    }
                }
            }

        client._get_json = fake_get_json
        status = await client.get_status()

        self.assertEqual(status.state, "started")
        self.assertEqual(status.query_status, "online")
        self.assertEqual(status.player_current, 3)
        self.assertEqual(status.player_max, 10)
        self.assertEqual(status.game_human, "ARK: Survival Evolved")
        self.assertTrue(status.is_online)

        await client.close()

    async def test_power_on_and_off_return_message(self):
        client = NitradoClient(token="x", service_id="123")

        async def fake_post_json(path):
            if path.endswith("/start"):
                return {"message": "server starting"}
            return {"message": "server stopping"}

        client._post_json = fake_post_json

        on_message = await client.power_on()
        off_message = await client.power_off()

        self.assertEqual(on_message, "server starting")
        self.assertEqual(off_message, "server stopping")

        await client.close()

    async def test_power_on_falls_back_to_restart_on_404(self):
        client = NitradoClient(token="x", service_id="123")
        calls: list[str] = []

        async def fake_post_json(path):
            calls.append(path)
            if path.endswith("/start"):
                raise NitradoApiError("Nitrado request failed (404): not found")
            if path.endswith("/restart"):
                return {"message": "server restarting"}
            raise AssertionError(f"Unexpected path: {path}")

        client._post_json = fake_post_json

        on_message = await client.power_on()

        self.assertEqual(on_message, "server restarting")
        self.assertEqual(
            calls,
            [
                "/services/123/gameservers/start",
                "/services/123/gameservers/restart",
            ],
        )

        await client.close()


if __name__ == "__main__":
    unittest.main()
