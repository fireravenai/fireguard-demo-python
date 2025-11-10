# fireguard-demo-python

Simple Demo of FireGuard integrated with an OpenAI assistant (Python) through a command-line interface.

## Features

- **Simple Chat Interface**: Easy-to-use command-line chat with OpenAI
- **FireGuard Integration**: Connected to FireGuard input and output guardrails
- **Conversation History**: Maintains message history throughout the session

## Documentation
Here is the documentation of FireGuard: https://doc.fireraven.ai/

## Installation

1. **Clone or download this repository**

2. **Create and activate a virtual environment**
    ```bash
   pip install virtualenv
   virtualenv env
   env/Scripts/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create an account on Fireraven and get your API Key and Project ID**
- Go to https://app.fireraven.ai/ and create an account
- Go to `Organizations` on the left side menu and click on the `Settings` of your organization
![Organizations page](images/image-0.png)
- Click on `Add API Key` and save the API Key
![Organization settings page](images/image-1.png)
- Go to `Projects` on the left side menu and click on `Add Project`
![Projects page](images/image-2.png)
- Click on the `Settings` of your project
- Find your `Project ID` and save it
![Project settings page](images/image-3.png)


5. **Set up your API keys**:
   
   Create a `.env` file in the project directory:
   ```bash
   # FireGuard API Configuration
   FIRERAVEN_PROJECT_ID=your_project_id
   FIRERAVEN_GUARDRAILS_API_KEY=your_fireraven_api_key

   # OpenAI API Key (can be changed to any other model you want to test in this repository)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. **Configure your FireGuard Topics Guardrail (Input Guardrail)**
- Go to `Projects` on the left side menu and click on the `Settings` of the project you want to configure
- Select the `Topics Guardrail`
![Topics Guardrail configuration](images/image-4.png)
- Click on `Create new topic`. The goal of the topics is to restrict which requests the agents can accept by topics. Some topics can be configured as safe and others as unsafe, to restrict the user from sending restricted requests, and to force the user to only send requests related to safe topics.
![Create new topic](images/image-5.png)
- To configure a topic, you first need to add a `Topic name` and a `Topic context prompt`. The context prompt is used to give more details about the context of the topic you want to configure.
- Afterwards, you can configure the `Questions` within this topic. The questions are used as data points to map the possible requests that are considered within this topic. The questions will allow to Topics Guardrail to perform better at classifying the requests from the user as safe or unsafe. You need a minimum of 1 question per topic.
- The `Questions` can be configured in 3 ways:
   - By adding a question manually
   - By generating questions automatically (the FireGuard platform will generate questions based on the Topic context prompt to map the possible questions a user could ask for this topic)
   - By uploading questions directly from a CSV file
- Afterwards, you can configure the `Validation questions`. The validation questions are used to measure the accuracy of a topic, by "simulating" questions that could be ask by a user. You need a minimum of 1 validation question per topic.
- The `Validation questions` can be configured in 3 ways:
   - By adding a validation question manually
   - By generating validation questions automatically (the FireGuard platform will generate validation questions based on the Topic context prompt to simulate real questions that could be ask by a user in a real-life scenario)
   - By uploading questions directly from a CSV file
- On the right panel of the topic configuration, you can set some additional parameters:
   - Applied to Input: a toggle to configure if the topic is applied to the Input Guardrails (on) or not (off)
   - Safe/Unsafe: a toggle to configure if the topic is safe or unsafe
   - Sensitivity: a slider to configure how permissive or restrictive the topic should be (A more permissive setting allows requests that differ more from the original questions. A more restrictive setting blocks requests that aren’t sufficiently similar.)
   - Accuracy: the accuracy is measured as the percentage of Validation Questions (simulating real users) that can be answered from the list of Questions, with the Sensitivity configured
- Once the configuration of the topic is done, click on `Save`


7. **Configure your FireGuard Policies Guardrail (Input and Output Guardrails)**
- Go to the `Policies` on the left side menu
![Policies page](images/image-6.png)
- To create a new custom policy, click on the `Add Policy` button
![Create new policy](images/image-7.png)
- In the interface to configure a custom policy you can see multiple things:
   - Name: The policy name should provide an immediate understanding of the policy at a glance.
   - Description: This description is essential for our system to accurately identify and measure the policy. The more precise the description, the more accurate the policy identification will be.
   - Criticality: Used to categorized incidents involving this policy.
   - Legitimate/Violation: Indicates whether a policy detection is safe or unsafe: detecting a legitimate policy is safe; detecting a violation triggers an issue; missing a legitimate policy triggers an issue; missing a violation is safe.
   - Detection threshold: Adjust how sensitive the detection is: a lower percentage catches more, a higher percentage catches only the strongest matches.
   - Test your policy: To validate the policy directly from the configuration interface.
- Once the policy is configured, you can click on `Create`
- To add a policy to a project, you can click on the green icon at the bottom right of a policy

![Add policy to project](images/image-8.png)
- You can also add a policy from the Project configuration page:
   - Go to `Projects` and click on the `Settings` of the project you want to configure
   - Select the `Policies Guardrail` tab
   - Click on the field `Add policy to project` to search for a policy to add to the project
- In the Project configuration page, you can also configure if the policies are to be applied to the Input or Output Guardrails or both. For example, a policy only applied to the input will only be triggered if the input message (from the user, sent to the assistant) violates the policy, but the policy won't look at the output message (from the assistant, back to the user).
![Configure policies for a project](images/image-9.png)


8. **Monitor the project**
- Go to the `Monitoring` on the left side menu
![Monitoring page](images/image-10.png)
- In the overview tab, you can see the issues detected related to the policies and the topics
- In the Messages tab, you can see the history of all messages monitored by FireGuard for this project
- In the Topics Analytics tab, you can see analytics on the topics of the messages
- You can click on the project name (top of the page) to change the project
- You can click on the settings wheel on the right of the project name (top of the page) to configure the project settings

<!-- - More information is available in the video here: 
[![Fireraven Demo Video](images/image-3.png)](https://www.youtube.com/watch?v=iqAqdHvMxmQ "Fireraven AI Security Suite Demo") -->


## Usage

Run the main script:
```bash
python main.py
```

### How to Use

- Once the application is running, simply type your message and press Enter to chat with the AI. The conversation history is maintained throughout the session.

- To exit the program, type `quit`, `exit`, or `bye`.

- If you want to stop the Input Guardrail from blocking the input message while you are testing, you can simply comment the lines 69-71 in the `openai_client.py` file:
```javascript=
69        # If input is blocked by guardrails, return a message
70        if not input_guardrails_response.get("is_safe", True):
71            return "Input blocked by input guardrail."
```

- If you want to stop the Output Guardrail from blocking the response message while you are testing, you can simply comment the lines 93-97 in the `openai_client.py` file:
```javascript=
93            # If output is blocked by guardrails, return a message
94            if not output_guardrails_response.get("is_safe", True):
95                apology_message = "Sorry, I can't answer your request as it goes against my policies."
96                self.add_message("assistant", apology_message)
97                return apology_message
```

## Project Structure

- `main.py` - Main application file with simplified command-line interface
- `openai_client.py` - OpenAI API client with message history management, and FireGuard Input/Output Guardrails integrated
- `fireguard_create_conversation.py` - FireGuard conversation creation utility
- `fireguard_input_guardrail.py` - FireGuard Input Guardrail integration
- `fireguard_output_guardrail.py` - FireGuard Output Guardrail integration
- `requirements.txt` - Python dependencies
- `.env` - Your API key configuration (create this file with your API keys)

## Requirements

- Python 3.7+
- OpenAI API key
- Fireraven API key
- Fireraven Project ID

## Dependencies

- `openai>=1.0.0` - Official OpenAI Python library
- `python-dotenv>=1.0.0` - For loading environment variables from .env files

