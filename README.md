Multiplayer Networking Architecture Comparison — Dissertation Prototypes

MSc Computer Science dissertation project, University of Bath.

Research Question: How do real-time networking architectures in multiplayer games maintain responsiveness and consistency under strict latency constraints, and how can these systems be evaluated and improved?

Overview

This repository contains two interoperating prototypes:

A network simulation and benchmarking toolkit — a real client-server system communicating over UDP sockets, with an injectable network impairment layer for simulating latency and packet loss under controlled, repeatable conditions.
A 2D fighting game prototype — the interactive testbed used to compare three competing synchronisation architectures under blind, controlled participant trials.

Fighting games were chosen as the target genre because they represent the most latency-sensitive class of multiplayer game, making architectural differences maximally observable.

Architectures under comparison
Client-side prediction + server reconciliation — Bernier (2001), Gambetta (n.d.)
Dead reckoning / entity interpolation — Aggarwal et al. (2004), Gambetta (n.d.)
Rollback netcode — Bernier (2001), Huynh and Valarino (2019)

Baseline condition: server-authoritative, no compensation, 0ms latency, 0% packet loss.

Project structure
Folder	Purpose
engine/	Shared game state, physics, and hit detection — common to all three strategies
network/	UDP transport layer and the Impairment Injector (latency/packet loss simulation)
strategies/	The three interchangeable synchronisation strategies
metrics/	Client- and server-side logging (state divergence, correction frequency, responsiveness)
session/	Orchestration layer — configures trials, launches client/server, manages participant sessions
server/	Server process entry point
client/	Client process entry point
tests/	Unit and integration tests
docs/	Design specification, architecture diagrams, supporting notes

Tech stack
Language: Python 3
Networking: built-in socket module (UDP)
Rendering: Pygame
Version control: Git / GitHub
