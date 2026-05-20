"""CLI for executing Khukra inference models from the terminal."""

import argparse
import json
import sys

from khukra.core.experiment import ExperimentRunner
from khukra.domains.registry import get_model, list_domains, list_models, list_subdomains


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute Khukra domain inference models")
    parser.add_argument("domain", choices=list_domains())
    parser.add_argument("subdomain", help="Subdomain within the domain")
    parser.add_argument("model", help="Model name within the subdomain")
    parser.add_argument("--params", help="JSON string of inference input overrides", default="{}")
    args = parser.parse_args()

    if args.subdomain not in list_subdomains(args.domain):
        available = ", ".join(list_subdomains(args.domain))
        print(f"Unknown subdomain '{args.subdomain}'. Available: {available}", file=sys.stderr)
        sys.exit(1)

    if args.model not in list_models(args.domain, args.subdomain):
        available = ", ".join(list_models(args.domain, args.subdomain))
        print(f"Unknown model '{args.model}'. Available: {available}", file=sys.stderr)
        sys.exit(1)

    model = get_model(args.domain, args.subdomain, args.model)
    params = json.loads(args.params)
    result = ExperimentRunner().run_once(model, params)

    print(json.dumps({"outputs": result.metrics, "inputs": result.parameters}, indent=2))


if __name__ == "__main__":
    main()
