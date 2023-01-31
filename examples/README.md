# Examples

## Initial Setup
bettercf requires initialisation, deploying some needed resources to your AWS account. See [what exactly is deployed here](https://github.com/ServerlessSam/bettercf/tree/main/.management/templates/bettercf-management).

After installing the CLI and configuring your AWS credentials, run the following command:

```bash
bettercf init
```

## Example 1

Example 1 shows you how to 'build' your Cloudformation template. This is an optional step that bettercf allows you to do. It leverages [dfm](https://github.com/ServerlessSam/data-file-merge) and allows you to logically seperate each Cloudformation resource into it's own file. Allowing for easier navigation, maintanance and readability when your templates become 1000's of lines long.

## Build a template
```bash
bettercf template build --name hello_world_app --dfm-config-path [LOCAL PATH TO THIS REPO]/.dfm/template_builder.json --dfm-root-path [LOCAL PATH TO THIS REPO]/examples/example_1
```
You will now see the built Cloudformation template at `[LOCAL PATH TO THIS REPO]/examples/example_2/template/hello_world_s3_bucket.json`.

## Example 2

Example 2 will push a Cloudformation template into the bettercf template repository. Reminder that you will need to **initialise** bettercf for this example to work.

## Push a template

```bash
bettercf template push --name hello-world-bucket --template-path [LOCAL PATH TO THIS REPO]/examples/example_2/template/hello_world_s3_bucket.json --template-version 1.0
```

If you navigate to the `cf-management-bucket-XXX` S3 bucket in your AWS account. You will now see your template file at `hello-world-bucket/1.0`. You have now pushed version 1.0 of this template to the bettercf template repository. Note that the template hasn't been deployed to Cloudformation yet. That is the next step.

## Deploy a stack

Now we are going to deploy a stack, referencing this versioned template in the bettercf template repository.
You can inspect the contents of `/examples/example_2/stack_config/hello_world_s3_config.json` to understand what we are deploying. Notice how we independantly version templates (`1.0`) and stacks (`0.1`).

```bash
bettercf stack deploy --stack-config-path [LOCAL PATH TO THIS REPO]/examples/example_2/stack_config/hello_world_s3_config.json
```

You can now see the stack deployed in Cloudformation and also see the `hello-world-bucket-XXX` bucket in your S3 console.