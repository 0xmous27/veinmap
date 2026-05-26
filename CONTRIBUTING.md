# Contributing to VeinMap

## How to Contribute

### Adding Checklists

1. Create a YAML file in `data/checklists/` following this format:

```yaml
service: service_name
ports: [port1, port2]
categories:
  enumeration:
    - id: unique_item_id
      description: "What this step does"
      command: "command with {IP} {USER} {PASS} placeholders"
      priority: high|medium|low
  exploitation:
    - id: ...
  post_exploitation:
    - id: ...
```

2. Submit a pull request.

### Adding Command References

1. Create or edit a YAML file in `data/commands/`:

```yaml
commands:
  category_name:
    - description: "What this command does"
      command: "command with {IP} {USER} {PASS} {HASH} {DOMAIN} {PORT} placeholders"
```

### Adding Report Templates

1. Create a Jinja2 template in `templates/` with `.md.j2` extension.
2. Available variables: `hosts`, `findings`, `timeline`, `credentials`, `pivots`, `total_hosts`, `owned_hosts`.

### Code Contributions

1. Fork the repo
2. Create a feature branch
3. Follow PEP 8 style
4. Add tests for new features
5. Submit a pull request

## Development Setup

```bash
git clone https://github.com/0xmous27/veinmap
cd veinmap
pip install -e .
pytest
```
