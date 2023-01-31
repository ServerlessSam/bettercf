# BetterCF

A CLI tool to improve your experience with Cloudformation templates and stacks.

# Installation Instructions

Each release of bettercf comes with a CLI binary for Windows, Mac and Linux. [Download the CLI file](https://github.com/ServerlessSam/bettercf/releases) required for your operating system. Finally, make sure that the dfm binary is available on your PATH. This process will differ depending on your operating system. See instructions for [mac/linux](https://stackoverflow.com/questions/14637979/how-to-permanently-set-path-on-linux-unix) and [windows](https://stackoverflow.com/questions/1618280/where-can-i-set-path-to-make-exe-on-windows).

To use the `init` and `push` mechanisms, ensure your environment is [configured with AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html). Ensure you are either using the `aws configure`, env var or default profile methods.

# Basic Usage

## Build Templates (Optional Step)
BetterCF allows you to use [data-file-merge (dfm)](https://github.com/ServerlessSam/data-file-merge) (also created by [@ServerlessSam](https://github.com/ServerlessSam)) to optionally build your Cloudformation template file from a directory tree.

```bash
bettercf template build --name MyAppStack --dfm-config-path /foo/bar/.dfm/config.json --dfm-root-path /foo/bar/mytemplates 
```
This will merge your directory tree into a single cloudformation template file. The logic used and location of merged file are dictated by the contents of `config.json`

## Push Templates
BetterCF needs you to push your templates into it's template repository. Similar to `docker push` pushing docker images into a container repository.

```bash
bettercf template push --name MyAppStack --template-path /foo/bar/mytemplates/myappstack.json --template-version 0.1
```

This will push the template found in `myappstack.json` into BetterCF's template repository with the name of `MyAppStack` and version of `0.1`. If you are using BetterCF in `Compliance` mode, this **cannot be undone**. Note this deploys nothing to Cloudformation.

## Deploy Stacks
Now we have pushed versioned templates into our BetterCF template repository (like pushing tagged docker images into a registry), it is time to deploy our stack (like deploying a container from a tagged image).

```bash
bettercf stack deploy --stack-config-path /foo/bar/stacks/myappstack-production.json
```

This command only needed one argument because **your stack configuration file contains all the information required to deploy your desired stack**.
# Hello World Example

See the `/examples` directory at the root of this repository.

## Why Use BetterCF

Problems using Cloudformation natively and how BetterCF solve these problems:
### There is no working 'out of the box' solution to automate deploying your stacks from day one

BetterCF provides the CI/CD automation required to get your stacks deploying via automation in minutes. It works by utilising it's CLI (which you can embed in your CI/CD pipeline yourself if you like!). Once everything is set up, you can release Cloudformation templates in the same way you release software and roll out those updates to new/existing stacks by simply creating/updating a stack configuration file in source control.
  
### Cloudformation does not support versioning your templates

BetterCF versions your **templates** when you 'push' them into the BetterCF template repository. It also versions your **stacks** when you 'deploy' them. The process is identical to how we all version our software and reference dependencies.
  
### How can you manage multiple environments that are relying on a single Cloudformation template? How do you ensure your envs are being updated as the template evolves over time?

All stack configuration files are checked into source control. This contains all the information you need in order to determine the state of every Cloudformation stack. Want to update your configuration (e.g use a newer version of a template)? Update the config file, raise a PR and merge!
  
### How do you support a use case where you need to deploy a stack with a slight variation from your established template? E.g A dev asks: 'can you deploy a version of App X for me to debug but enable SSH access?'

Your stack configuration file contains a `ResourceOverrides` section. You can use this section to make any changes to resources from the referenced template, without making those changes to the template itself. **(Note this is coming soon!)**
  
### Cloudformation usage is very difficult to audit and maintain compliance

When your initialize BetterCF, you have the options to use `Standard`, `Govern` or `Compliance` mode. Each coming with more restrictions than the previous. In compliance mode, your templates pushed into the BetterCF template repository are **immutable**. And your git history is your breadcrumb trail of what changes were made to your Cloudformation stacks, when, and by who.
