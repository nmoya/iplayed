import asyncio

from deployment import DeployError, deploy_completions
from file_persistence import clear_pending_deploy
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class DeployPromptScreen(ModalScreen[str]):
    CSS = """
    DeployPromptScreen {
        align: center middle;
    }

    #deploy-dialog {
        width: 80;
        height: auto;
        padding: 2;
        background: $surface;
        border: thick $primary;
    }

    #deploy-actions {
        height: auto;
        margin-top: 1;
    }

    #deploy-actions Button {
        margin-right: 1;
    }

    #deploy-status {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "postpone", "Postpone deploy"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("completions.json has changes pending deploy."),
            Input(placeholder="Deploy message", id="deploy-message"),
            Horizontal(
                Button("Deploy now", id="deploy", variant="primary"),
                Button("Postpone deploy", id="postpone"),
                Button("Delete Marker", id="delete-marker", variant="error"),
                id="deploy-actions",
            ),
            Static("", id="deploy-status"),
            id="deploy-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#deploy", Button).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deploy":
            await self.action_deploy()
        elif event.button.id == "postpone":
            self.action_postpone()
        elif event.button.id == "delete-marker":
            self.action_delete_marker()

    async def on_input_submitted(self, _: Input.Submitted) -> None:
        await self.action_deploy()

    async def action_deploy(self) -> None:
        message = self.query_one("#deploy-message", Input).value.strip()
        status = self.query_one("#deploy-status", Static)
        if not message:
            status.update("Deploy message is required.")
            self.query_one("#deploy-message", Input).focus()
            return

        status.update("Deploying completions.json...")
        self.query_one("#deploy", Button).disabled = True
        try:
            await asyncio.to_thread(deploy_completions, message)
        except DeployError as exc:
            status.update(f"Deploy failed: {exc}")
            self.query_one("#deploy", Button).disabled = False
            return

        self.dismiss("deployed")

    def action_postpone(self) -> None:
        self.dismiss("postponed")

    def action_delete_marker(self) -> None:
        clear_pending_deploy()
        self.dismiss("deleted")
