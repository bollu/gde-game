# gpt2-converse

# Screenshot
![screenshot](./screenshot.png)

# Analysis of the game

![feedback1](./feedback1.jpg)
![feedback2](./feedback2.jpg)

The game was interesting to all players. People found it engaging and 
entertaining due to the inherent unpredicability of the chatbot. We could have
made the experience much more realsitic if we could have had:

- A larger model for more coherent text, and the ability to retain more of 
  the context of the conversation

- More time to fine-tune the model towards the topics we were interested in.
  Some compute power spent in fine-tuning makes the model output much more
  realistic

There was some divide over the interface. Some people enjoyed the old school
retro inteface of typing into the terminal. Others felt that the experience
would have been much better if we had a GUI. We unfortunately had technical
considerations for why we could not build a GUI: The model that powers the
chat engine runs on the local `ada` servers that block HTTP access. Hence,
we were running the whole game over SSH. However, we can in the future move
the model to google cloud and thereby get some more performance.


# [Game design document](./Game-design-document.docx)

# Introduction

Use GPT-2 To try and simulate a conversation between a person and an immigration officer.
Topic chosen due to the fact that GPT-2 appears to be trained on a corpus of text that knows an
unusual amount about wars, famine, death, american politics, and the middle east.

We attempt to prime GPT-2 by setting up the "context" of the person who is being interviewed.
We then append the entire transcript and ask GPT-2 to continue the conversation.

# Team photo
![team-photo](./team-photo.jpg)

<img src="team-photo.jpg" width="128">


# Results:

Mixed. sometimes it's very coherent, other times it's not as much....

# Installation instructions
TODO: write script
