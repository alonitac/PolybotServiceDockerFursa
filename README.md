# The Polybot Service: Docker Project [![][autotest_badge]][autotest_workflow]

## Background and goals

In the [previous Python project][PolybotServicePython], you developed a chatbot application which applies filters to images sent by users to a Telegram bot.

In this project, you extend the service to detect objects in images, and send the results to clients.
You'll design, develop and deploy a service consisted by multiple containerized microservices, as follows: 

- `polybot`: Telegram Bot app.
- `yolo5`: Image object detection container based on the Yolo5 pre-train deep learning model.
- `mongo`: MongoDB cluster to store data.

## Preliminaries

1. Fork this repo by clicking **Fork** in the top-right corner of the page. 
2. Clone your forked repository by:
   ```bash
   git clone https://github.com/<your-username>/<your-project-repo-name>
   ```
   Change `<your-username>` and `<your-project-repo-name>` according to your GitHub username and the name you gave to your fork. E.g. `git clone https://github.com/johndoe/PolybotServiceDocker`.
3. It is a good practice to create an isolated Python virtual environment specifically for your project. 
   [Configure a new Python virtual environment in PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html).

Later on, you are **required** to change the `README.md` file content to provide relevant information about your service project, e.g. how to launch the app, main features, etc.

Let's get started...

## Guidelines

### The `mongo` microservice

MongoDB is a [document](https://www.mongodb.com/document-databases), [NoSQL](https://www.mongodb.com/nosql-explained/nosql-vs-sql) database, offers high availability deployment using multiple replica sets.
**High availability** (HA) indicates a system designed for durability and redundancy.
A **replica set** is a group of MongoDB servers, called nodes, containing an identical copy of the data.
If one of the servers fails, the other two will pick up the load while the crashed one restarts, without any data loss.

Follow the official docs to deploy containerized MongoDB cluster on your local machine. 
Please note that the mongo deployment should be configured **to persist the data that was stored in it**.

https://www.mongodb.com/compatibility/deploying-a-mongodb-cluster-with-docker

Got HA mongo deployment? great, let's move on...

### The `yolo5` microservice

[YoloV5](https://github.com/ultralytics/yolov5) is a state-of-the-art object detection AI model. It is known for its high accuracy object detection in images and videos.
You'll work with a lightweight model that can detect [80 objects](https://github.com/ultralytics/yolov5/blob/master/data/coco128.yaml) while it's running on your old, poor, CPU machine. 

The service files can be found under the `yolo5` directory.
The `yolo5/app.py` file is a Flask-based webserver, with an endpoint `/predict`, which can be used to predict objects in a given image, as follows:

```text
localhost:8081/predict?imgName=street.jpeg
```

The `imgName` query parameter value (`street.jpeg` in the above example) represents an image name stored in an **S3 bucket**. 
The `yolo5` service then downloads the image from the S3 bucket and detects objects in it. 

Take a look on the code, and complete the `# TODO`s. Feel free to change/add any functionality as you wish!

> [!NOTE]
> If you attempt to run the `yolo5` service locally, not as a Docker container, you'll encounter errors since the app depends on many files that don't exist on your local machine, but do exist in the [`ultralytics/yolov5`](https://hub.docker.com/r/ultralytics/yolov5) Docker image.  
> Thus, it's recommended first to containerize the app then run it as a container. [Read here](https://github.com/ultralytics/yolov5) if you still want to work hard and run it uncontainerized. 


To containerize the app, take a look at the provided `Dockerfile`, it's already implemented for you, no need to touch.

When running the container on your local machine, you may need to **mount** the directory containing the AWS credentials on your local machine (`$HOME/.aws/credentials`) to allow the container communicate with S3.

**Note: Never build a docker image with AWS credentials stored in it! Never commit AWS credentials in your source code! Never!**

Once the image was built and run successfully, you can communicate with it directly by:

```bash
curl -X POST localhost:8081/predict?imgName=street.jpeg
```

For example, here is an image and the corresponding results summary:

<img src="https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_street.jpeg" width="60%">

```json
{
    "prediction_id": "9a95126c-f222-4c34-ada0-8686709f6432",
    "original_img_path": "data/images/street.jpeg",
    "predicted_img_path": "static/data/9a95126c-f222-4c34-ada0-8686709f6432/street.jpeg",
    "labels": [
      {
        "class": "person",
        "cx": 0.0770833,
        "cy": 0.673675,
        "height": 0.0603291,
        "width": 0.0145833
      },
      {
        "class": "traffic light",
        "cx": 0.134375,
        "cy": 0.577697,
        "height": 0.0329068,
        "width": 0.0104167
      },
      {
        "class": "potted plant",
        "cx": 0.984375,
        "cy": 0.778793,
        "height": 0.095064,
        "width": 0.03125
      },
      {
        "class": "stop sign",
        "cx": 0.159896,
        "cy": 0.481718,
        "height": 0.0859232,
        "width": 0.053125
      },
      {
        "class": "car",
        "cx": 0.130208,
        "cy": 0.734918,
        "height": 0.201097,
        "width": 0.108333
      },
      {
        "class": "bus",
        "cx": 0.285417,
        "cy": 0.675503,
        "height": 0.140768,
        "width": 0.0729167
      }
    ],
    "time": 1692016473.2343626
}
```

The model detected a _person_, _traffic light_, _potted plant_, _stop sign_, _car_, and a _bus_. Try it yourself with different images.

### The `polybot` microservice

Now let's integrate the `polybot` microservice with the `yolo5`. The integration is done as follows:

1. Clients send images to the Telegram bot.
2. The `polybot` microservice receives the message, downloads the image to the local file system, and uploads it to an S3 bucket.
3. The `polybot` microservice then initiates an HTTP request to the `yolo5` microservice, and waits for the response. 
4. Once the response arrived, the `polybot` microservice parse the returned JSON and sends the results to the client, in any form you like.

Here is an end-to-end example of how it may look like:

<img src="https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_polysample.jpg" width="30%">

You are highly encouraged to leverage your code implementation from the previous [Python project][PolybotServicePython], or alternatively, to use the code sample given to you under `polybot/` directory.
To get some guidance on how to implement the code, take a look at the `# TODO`s in `polybot/bot.py` file.

## Deploy the service for Prod and Dev in a single EC2 instance as a Docker Compose project

To simplify the deployment process, we'll create a Docker Compose project in the `docker-compose.yaml` file. 
This file will enable you to launch all 3 microservices with a single command: `docker compose up`.

Since **the same** `docker-compose.yaml` project file is being used **for both Prod and Dev envs**, 
avoid specifying manual env-related values. Instead, provide env-related values (e.g. bot token, image name and tag, bot URL) as environment variables using `.env` file.  

[An `.env` file in Docker Compose](https://docs.docker.com/compose/environment-variables/set-environment-variables/) is a text file used to define environment variables that available when running `docker compose up`. 

Here's an example of how your `.env` file might look like:

```text
# .env file

POLYBOT_IMG_NAME=polybot:v123
YOLO5_IMG_NAME=yolo5:v123
TELEGRAM_APP_URL=https://dev-bot.mydomain.click
```

And here's how you use it in the compose file:

```yaml
# docker-compose.yaml

services:
  polybot:
    image: ${POLYBOT_IMG_NAME}
```

That way you won't need to directly edit your `docker-compose.yaml` file each time you build a new version of your images.

Finally, deploy the compose project in a single `medium` Ubuntu EC2 instance with 20GB disk.
In general, you should have 2 different EC2 `medium` instances, one for Dev bot, one for Prod bot. 


#### Deployment notes

- You can expose the polybot to Telegram servers using you domain, as done in the previous project.
- Don't configure your compose file to build the images. Instead, push the `yolo5` and `polybot` images to a public DockerHub repo and use these images. 
- Attach an IAM role to your EC2 instance with the relevant permissions (E.g. read/write access to S3). Don't manage AWS credentials yourself, and never hard-code AWS credentials in the `docker-compose.yaml` file. 
- Don't hard-code your telegram token in the compose file, this is a sensitive data. [Read here](https://docs.docker.com/compose/use-secrets/) how to do it properly.  
- Build a robust code. Implement **retry** and **timeout** mechanism when needed, handle error properly. Test your app under failure - does the polybot keep work even if the yolo5 is down? Is yolo5 crashing when the mongo cluster is not initialize? etc...
- Strive to create your Docker images as small as possible.
- Try to automate the Mongo cluster initialization, so you don't need to manually connect to the container and initialize the cluster.
- Use `snyk` to search (and potentially clean) for any `HIGH` and `CRITICAL` security vulnerabilities.

## Integrate a simple CI/CD pipeline using GitHub Actions

The GitHub Actions workflows are already written for you and available under `.github/workflows/service-deploy-[dev|prod].yaml`. Take a moment to review it, and **customize it** according to your specific requirements.

   The workflow expects some secrets to be available:
   - Go to your project repository on GitHub, navigate to **Settings** > **Secrets and variables** > **Actions**.
   - Click on **New repository secret**.
   - Define the following secret values:
     - `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD` - Only if you use DockerHub to store images.
     - `EC2_SSH_PRIVATE_KEY` - The private key value to connect to your EC2.
     - `TELEGRAM_BOT_TOKEN` - The Telegram bot token.

Check that your CI/CD pipeline works properly for both Dev and Prod using the same Git flow used in the previous project.


## Submission

Once the **Polybot Service Deployment Dev** workflow is completed, the **Project auto-testing** workflow would be triggered automatically and test your project. 

So no further steps should be taken to pass the automated testing :-)

As always, if there are any failures, click on the failed job and **read the test logs carefully**. Fix your solution, commit and push again.

**Note:** Your EC2 instances should be running while the automated test is performed. **Don't forget to turn off the machines when you're done**.

## Good Luck


[autotest_badge]: ../../actions/workflows/project_auto_testing.yaml/badge.svg?event=push
[autotest_workflow]: ../../actions/workflows/project_auto_testing.yaml/
[github_actions]: ../../actions

[PolybotServicePython]: https://github.com/alonitac/PolybotServicePythonFursa
[docker_project_street]: https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_street.jpeg
[docker_project_polysample]: https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_polysample.jpg
