#!/usr/bin/env python3

from openai import OpenAI
import os
import requests
import argparse
import sys
from anthropic import Anthropic
from typing import List, Dict

api_key_claude = os.environ.get("CLAUDE_API_KEY")
api_key_openAI = os.environ.get("OPENAI_API_KEY")

class ClaudioConversation:
    def __init__(self, model="claude-3-haiku-20240307", max_tokens=4000):
        """
        Initialize a conversation with Claude.
        
        Args:
            model (str): The Claude model to use
            max_tokens (int): Maximum tokens for the conversation
        """
        self.client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role (str): 'user' or 'assistant'
            content (str): The message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_conversation_history(self):
        """
        Return the current conversation history.
        
        Returns:
            List[Dict[str, str]]: Conversation messages
        """
        return self.conversation_history
    
    def clear_history(self):
        """
        Clear the entire conversation history.
        """
        self.conversation_history = []
    
    def truncate_history(self):
        """
        Truncate conversation history if it exceeds max tokens.
        This is a simple implementation and might need more sophisticated 
        token counting in a production environment.
        """
        while sum(len(msg['content']) for msg in self.conversation_history) > self.max_tokens:
            # Remove the oldest message, keeping the most recent context
            self.conversation_history.pop(0)
    
    def send_message(self, user_input: str) -> str:
        """
        Send a message and get Claude's response while maintaining context.
        
        Args:
            user_input (str): The user's message
        
        Returns:
            str: Claude's response
        """
        try:
            # Add user message to history
            self.add_message("user", user_input)
            
            # Truncate history if needed
            self.truncate_history()
            
            # Send message to Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=self.conversation_history
            )
            
            # Extract the response text
            response_text = response.content[0].text
            
            # Add Claude's response to history
            self.add_message("assistant", response_text)
            
            return response_text
        
        except Exception as e:
            return f"An error occurred: {str(e)}"


class OpenAIConversation:
    def __init__(self, model="gpt-3.5-turbo", max_tokens=1000):
        """
        Initialize an OpenAI conversation client.
        
        Args:
            model (str): The OpenAI model to use
            max_tokens (int): Maximum tokens for the conversation
        """
        # Initialize the OpenAI client
        # Expects OPENAI_API_KEY to be set as an environment variable
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role (str): 'user', 'assistant', or 'system'
            content (str): The message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def send_message(self, user_input: str) -> str:
        """
        Send a message and get OpenAI's response while maintaining context.
        
        Args:
            user_input (str): The user's message
        
        Returns:
            str: OpenAI's response
        """
        try:
            # Add user message to history
            self.add_message("user", user_input)
            
            # Send message to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=self.max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Add assistant's response to history
            self.add_message("assistant", response_text)
            
            return response_text
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def clear_history(self):
        """
        Clear the entire conversation history.
        """
        self.conversation_history = []


# Add closing statement later
def getResponse(input, model, gpt, claude):
    if model == 'gpt':
        response = gpt.send_message(input)
        print("GPT:\n")
        print(response)
    elif model == 'claude':
        response = claude.send_message(input)  # Assume there is a method send_message in claude, too.
        print("CLAUDE:\n")
        print(response)
    else:
        response = "Model not supported"
    return response
  

def main():
    parser = argparse.ArgumentParser(description = 'Dialogue between claude and chatgpt for n number of iterations')

    parser.add_argument("-m", "--model", help = 'The type of model, claude or gpt', required = True)
    parser.add_argument("-i", "--iterations", type=int, help = 'The number of iterations between the two models', required = True)
    parser.add_argument("-s", "--start", help = 'The starting message to the conversation', required = True)


    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    model1 = ''
    model2 = ''

    if(args.model == "gpt"):
        model1 = "gpt"
        model2 = "claude"
    elif(args.model == "claude"):
        model1 = "claude"
        model2 = "gpt"

    iterations = args.iterations
    input = args.start

    convClaude = ClaudioConversation()
    convGpt = OpenAIConversation()

    #if statement to assign model1 and model2 based off args
    input = args.start
    it = args.iterations
    while(it > 0):
      input = getResponse(input,model1,convGpt,convClaude)
      input = getResponse(input,model2,convGpt,convClaude)
      it -= 1

if __name__ == "__main__":
    main()