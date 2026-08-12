# Tread Lightly

Protects secrets and sensitive data during `.env`, configuration, credential, log, Git, and related file operations. It minimizes access, suppresses secret values, prevents unnecessary persistence or transmission, and displays a turn-scoped `Tread Lightly` mode footer whenever active. Sensitivity is triaged per file, never per target, so non-sensitive files in a mixed directory are handled normally and completely; every footer turn discloses in one short phrase why the mode is active. Echoing file contents through a redaction filter is explicitly forbidden as a substitute for minimal reading -- an output-side filter is a denylist that only catches the secret shapes guessed in advance -- and the skill names the carriers credentials actually hide in, including URL query strings, connection strings, headers, and prefixless high-entropy values, on the principle that a field's key name is not a reliable signal. Its model-field helper can return one validated model identifier from JSON or TOML without dumping unrelated configuration.

## Related skills

- None required. The one-response footer lifecycle mirrors `initialize`, but Tread Lightly activates explicitly or automatically on each sensitive turn.
