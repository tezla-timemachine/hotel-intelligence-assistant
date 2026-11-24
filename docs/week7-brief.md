# Week 7 – Multimodal Hotel Intelligence Assistant (the course brief, as given)

*Copied from the brief pasted into the chat on 23 Nov 2026. The text is unchanged; only headings and list formatting were added.*

## Project Title
Multimodal Hotel Intelligence Assistant

## Business Scenario
A hotel group has customer reviews together with hotel images.
Management wants to search and understand both the written feedback and the related images in one system.
For example:
- "Show me room images related to negative reviews."
- "Find hotel facilities associated with positive feedback."
- "Show images related to complaints about public areas."
- "What are customers saying about the rooms shown in these images?"

The goal is to build a multimodal system that understands both images and text.

## Dataset
Use the ViMACSA multimodal hotel dataset.
Dataset Repository:
- https://github.com/hoangquy18/Multimodal-Aspect-Category-Sentiment-Analysis
- https://drive.google.com/file/d/1OjWwzdbhvhYc864Tpt6Xw9anBLfgNwmt/view?usp=sharing&utm_source=chatgpt.com

The complete dataset contains thousands of documents and around 14,000 images.
You do not need to process the complete dataset.
For this project, take approximately:
- 500 images
- A small selected set of review documents

Keep the project manageable and focus on understanding the multimodal pipeline rather than processing every available record.

## Main Product Goal
Build a system where a user can search hotel information using natural language.
The application should understand both:
- Text
- Images

The system should return relevant images, related reviews, and a short answer based on the retrieved information.

## Step 1: Prepare the Dataset
Select around 500 images and a manageable number of associated reviews.
Keep the connection between every image and its related review.
Review what information is actually available before creating the final dataset.
Do not create fields that are not present in the source unless you clearly mark them as generated information.

## Step 2: Image Understanding
Use a Vision Language Model such as ChatGPT Vision or Moondream.
Generate a short description for each selected image.
For example:
- Room interior
- Swimming pool
- Restaurant food
- Lobby
- Hotel facility
- Public area

Store the image description together with the original image and related review.

## Step 3: Multimodal Embeddings
Create embeddings for the images and text.
You can use a multimodal embedding model such as CLIP or SigLIP.
The purpose is to place images and text in a similar semantic space.
This allows a text query to retrieve relevant images.

## Step 4: Vector Database
Store the multimodal embeddings in a vector database.
Each record should remain connected to:
- Image
- Image description
- Related review
- Relevant metadata

This will allow semantic search across the dataset.

## Step 5: Natural Language Search
Create a simple search interface.
Examples:
- "Show room images associated with negative feedback."
- "Find images related to good hotel facilities."
- "Show public areas mentioned in negative reviews."
- "Find images connected with positive comments about food."

The system should return the most relevant results.

## Step 6: Multimodal RAG
Add a multimodal RAG layer.
The system should first retrieve relevant images and reviews.
Then a Vision Language Model or LLM should generate an answer using only the retrieved information.
Example:
User: "What are the main complaints about the rooms shown in these images?"
The system should retrieve the relevant room images and reviews and generate a short answer.

## Step 7: Evaluate the Search
Create around 20 to 30 test queries.
For each query, manually identify what type of result should be relevant.
Measure:
- Precision at K
- Retrieval accuracy
- Response time
- Incorrect retrievals

Check whether the returned images actually match the user's request.

## Step 8: Compare Different Approaches
Compare at least two approaches.
For example:
- Text search using generated captions
- Multimodal embedding search

You can also compare CLIP and SigLIP if time allows.
Create a simple comparison table.

| Approach | Retrieval Quality | Response Time | Notes |
|---|---|---|---|
| Caption Search | | | |
| Multimodal Search | | | |

Explain which approach works better and why.

## Step 9: Failure Analysis
Review the searches that perform badly.
Check whether:
- The image was misunderstood
- The review was unrelated to the image
- The embedding returned visually similar but irrelevant images
- The query was too broad
- The system misunderstood the relationship between text and image

Document a few important failure cases and possible improvements.

## Step 10: User Interface
Create a simple application with:
- Search box
- Retrieved image gallery
- Related review text
- Similarity score
- Short AI generated answer

The main experience should be simple:
- User asks a question
- System searches images and text
- System returns the relevant evidence
- System generates an answer

## Final Deliverables
- Selected multimodal dataset
- Approximately 500 images
- Selected review documents
- Image understanding pipeline
- Multimodal embeddings
- Vector database
- Natural language search
- Multimodal RAG
- Evaluation queries
- Retrieval evaluation
- Model or approach comparison
- Failure analysis
- Simple user interface
- GitHub repository

## Main Learning Outcome
At the end of Week 7, you should understand how text and images can be used together inside one AI product.
You should understand:
- Vision Language Models
- Multimodal embeddings
- Text to image retrieval
- Image to text understanding
- Semantic visual search
- Multimodal RAG
