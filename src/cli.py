import argparse
import json
from pathlib import Path

from dfm.file_types import JsonFileType

from src.initialisation import BetterCfInstance
from src.stack import Stack
from src.template import Template
from src.version import Version


def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(description="#TODO")
    parser.add_argument(
        "--version",
        help="Reveal CLI version.",
        action="version",
        version="%(prog)s {version}".format(version="TODO"),
    )

    # create sub-parser
    sub_parsers = parser.add_subparsers(
        help="sub-command help", dest="main_subparser_name"
    )

    # create the parser for the "init" sub-command
    parser_init = sub_parsers.add_parser(
        "init", help="Initialize BetterCF in your AWS account."
    )
    parser_init.add_argument(
        "--mode",
        "-m",
        default="standard",
        choices=["standard", "compliance", "governance"],
        help="Initialises BetterCF in standard, compliance or governance mode.",
    )

    # create the parser for the "teardown" sub-command
    parser_teardown = sub_parsers.add_parser(
        "teardown", help="Remove all BetterCF resources from your AWS account."
    )
    parser_teardown.add_argument(
        "--force",
        "-f",
        action="store_true",
        help='Will attempt to empty S3 buckets before teardown. Note this will still fail if BetterCF was initialized in "compliance" or "governance" mode. You must delete all S3 objects manually.',
    )

    # create the parser for the "template" sub-command
    parser_template = sub_parsers.add_parser(
        "template", help="subcommand for building/pushing templates"
    )

    # create the parser for the "stack" sub-command
    parser_stack = sub_parsers.add_parser(
        "stack",
        help="subcommand for deploying individual stacks from a pushed template.",
    )

    # create sub-parser for sub-command template
    template_sub_parsers = parser_template.add_subparsers(
        dest="secondary_subparser_name", help="sub-sub-command help"
    )

    # create sub-command "build" for sub-command cool
    parser_def_build = template_sub_parsers.add_parser(
        "build",
        help="(optional step if using DFM) build template from directory files.",
    )
    parser_def_build.add_argument(
        "--name", "-n", required=True, help="name of the template"
    )
    parser_def_build.add_argument(
        "--dfm-config-path",
        "-c",
        required=True,
        help="complete local path to a dfm config file defining the file merge.",
    )
    parser_def_build.add_argument(
        "--dfm-root-path",
        "-r",
        required=True,
        help="complete local path to the root path the dfm merge should start from.",
    )
    # parser_def_build.add_argument('--auto-push', '-p', action='store_true', help='Will automatically push your built template to your BetterCF management bucket.')

    # create sub-command "push" for sub-command cool
    parser_def_push = template_sub_parsers.add_parser(
        "push", help="push CloudFormation template to the BetterCF management bucket."
    )
    parser_def_push.add_argument(
        "--name", "-n", required=True, help="name of the template"
    )
    parser_def_push.add_argument(
        "--template-path",
        "-t",
        required=True,
        help="complete local path to the CloudFormation template to push.",
    )
    parser_def_push.add_argument(
        "--template-version",
        "-v",
        default=False,
        help='The version tag that this template should be pushed with. E.g "1.0.0".',
    )

    # create sub-parser for sub-command stack
    stack_sub_parsers = parser_stack.add_subparsers(
        dest="secondary_subparser_name", help="sub-sub-command help"
    )

    # create sub-command "deploy" for sub-command cool
    parser_stack_deploy = stack_sub_parsers.add_parser(
        "deploy",
        help="(optional step if using DFM) build template from directory files.",
    )
    parser_stack_deploy.add_argument(
        "--stack-config-path",
        "-c",
        required=True,
        help="complete path to the stack config file.",
    )

    args = parser.parse_args()
    if args.main_subparser_name == "init":
        cf = BetterCfInstance()
        cf.initialise(args.mode.upper())
    elif args.main_subparser_name == "teardown":
        cf = BetterCfInstance()
        cf.teardown(args.force)
    elif args.main_subparser_name == "template":
        if args.secondary_subparser_name == "build":
            template = Template(
                args.name, Path(args.dfm_config_path), Path(args.dfm_root_path)
            )
            template.build()
        elif args.secondary_subparser_name == "push":
            Template.push_mechanism(
                name=args.name,
                version=Version(args.template_version),
                template_str=json.dumps(
                    JsonFileType.load_from_file(args.template_path)
                ).encode("utf-8"),
            )
        else:
            raise Exception(
                f"CLI command ({args.main_subparser_name} {args.secondary_subparser_name}) is not recognized."
            )
    elif args.main_subparser_name == "stack":
        if args.secondary_subparser_name == "deploy":
            cfg = Stack.load_stack_config_from_file(Path(args.stack_config_path))
            cfg.deploy()
        else:
            raise Exception(
                f"CLI command ({args.main_subparser_name} {args.secondary_subparser_name}) is not recognized."
            )


if __name__ == "__main__":
    main()
