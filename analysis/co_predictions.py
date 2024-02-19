import pandas as pd 
from edsl.questions import QuestionFreeText
from edsl import Scenario, Survey, Agent, Model
from edsl.results import Results
import csv

file_path = '../etl/data/articles_formatted.csv'

data = []
with open(file_path, "r") as f: 
    reader = csv.reader(f)
    header = next(reader)
    for row in reader: 
        data.append(row)

df = pd.DataFrame(data, columns=["index", "title", "abstract", "paragraph", "pub_date", "sentence1", "sentence2"])

df = df[["title", "sentence1", "sentence2"]]
df

def add_content(df):

    # We create questions prompting the agent to provide the next sentence and to draft the next sentence
    q_draft = QuestionFreeText(
        question_name = "draft",
        question_text = """Consider a recent news article \'{{ title }}\' that begins: {{ sentence1 }}.
        Draft the end of the sentence or the next sentence in this article."""
    )

    # We create scenarios of the questions with the article titles and first sentences
    scenarios = [Scenario({"title":row["title"], "sentence1":row["sentence1"]}) for _, row in df.iterrows()]

    # We create an agent that has total recall of recent articles and an agent that is capable of drafting an article
    agents = [
        Agent(name="total_recall", traits={"persona":"You have total recall of recent news articles."}),
        Agent(name="great_writer", traits={"persona":"You are a world-class news journalist."})
    ]

    # We combine the questions into a survey
    survey = Survey(questions=[q_draft])

    # We select an LLM
    model = Model('gpt-4-1106-preview')

    # We administer the survey with the data to both agents -- questions are administered asynchronously 
    results = survey.by(scenarios).by(agents).by(model).run()
    
    return results

results = add_content(df)

df_results = results.to_pandas()
df_combined = pd.merge(df, df_results, left_on='sentence1', right_on='scenario.sentence1', how='inner')

# In general, choose output from "you have total recall" if you have total recall answer begins with "I'm sorry, but I" 
# then use output from "you are a worldclass journalist"

# Filter the DataFrame to drop rows where 'answer.draft' starts with "I'm sorry, but"
df_filtered = df_combined[~df_combined['answer.draft'].str.startswith("I'm sorry, but")]

# Sort the DataFrame based on 'agent.agent_name' column in descending order
# This will put 'total_recall' first and 'great_writer' second for each title
df_filtered = df_filtered.sort_values(by='agent.agent_name', ascending=False)
# Drop duplicates based on the 'title' column, keeping the first occurrence
df_final = df_filtered.drop_duplicates(subset='title', keep='first')

# Select the desired columns
df_final = df_final[["title", "sentence1", "sentence2", "answer.draft", "agent.agent_name", "prompt.draft_system_prompt", "prompt.draft_user_prompt"]]
print(df_final)
df_final.to_csv('../etl/data/articles_predictions.csv', index=False)
