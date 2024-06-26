from openai import OpenAI
from datetime import datetime
import csv



client = OpenAI(api_key='''INSERT KEY''')
FILEPATH = input('Student Responses File: ')
RESPONSES = {} # global dictionary with all questions : responses.


# sends a ChatGPT call with context and prompt
def callAPI(context, prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

# read in the CSV file and look for "Student Name" and "Response" Columns
def readCSV(filename):
    responses = ''
    try:
        with open(filename, mode='r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                formatted_response = f"{row['Student Name']}: {row['Answer 1']}\n"
                responses += formatted_response
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except KeyError as e:
        print(f"Error: Missing column in CSV file - {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    csvfile.close()
    return responses

def readText(filename):
    # just in case I need to call all individual responses to a certain question.  
    def splitResponses(string : str):
        lines = string.strip().split('\n')
        if lines[0] in RESPONSES:
            RESPONSES[lines[0]].extend(lines[1:])
        else: RESPONSES[lines[0]] = lines[1:]

    try:
        with open(filename, mode='r') as txtfile:
            string = txtfile.read()
            splitResponses(string)
            return string
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read file '{filename}'!")
        return None
    except IsADirectoryError:
        print(f"Error: Expected a file but found a directory '{filename}'!")
        return None
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
        return None


# context and prompt

''' JUNE 13th
PROMPT WORK:
: Anonymize data
TODO: Can you measure how well students are comprehending the subject? Also take this into account. ie. "Read through the student's responses, can you scale how good their comprehension is? Can you identify any gaps in their learning?"
: Do not isolate any individual student
'''


''' JUNE 17th
- Work with Michelle to get the API set up properly. Usage is too low atp. Don't worry about low/no cost.
- Ping Michelle on slack, figure out a cost-effective way to call to the API
- For sake of teams, try to reduce cost below $50
'''
context = "You are a teacher at an entrepreneurship and tech camp asking students about their day, looking for signs of stress and how well they understood the material. Among other common signs, stress may be induced by students overwhelmed by the work ahead, not feeling comfortable in their project groups, or students feeling disinterested in the work they are doing. Your goal is to identify how tense the entire class is feeling."
#prompt = "Provide a summary using the responses below to identify why students feel stressed. Then, can you measure how good the student's comprehension is while finding any gaps in their learning?"
prompt = "In the responses below, the question is on the first line and answers are on following lines. Provide a summary using the responses to identify the level of comprehension of the students. Then, can you measure the overall comprehension of the students (perhaps on a one to ten scale)? Finally, please try to identify any gaps in the student's learning. List any gaps in student learning. Use only the questions and responses provided below, do not mention topics unless students explicitly speak about them.: \n\n"

if FILEPATH.endswith('.csv'):
    student_responses = readCSV(FILEPATH)
elif FILEPATH.endswith('.txt'):
    student_responses = readText(FILEPATH)
else: 
    raise TypeError("Please input the path to a .csv or .txt file.")


if student_responses:
    full_prompt = prompt + student_responses
    print(f"=========== FULL PROMPT:\n\n{full_prompt}\n\n")
    response = callAPI(context, full_prompt)

    # prints GPT's responses to terminal
    print(response)

    # save to a new .txt file
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"GPT-Responses.txt"
    with open(filename, "a") as file:
        file.write(f"Response at {current_datetime} with filename = {FILEPATH.split('/')[-1]}: \n{response}\n\n") # TODO: might have to change FILEPATH index as front-end might take in just filename and not path
        file.close()
    print(f"Response saved to {filename}")
else:
    print("Failed to read student responses!")
