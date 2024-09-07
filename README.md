# taxi_app

Taxi Application with customer and driver mobile apps, built using a microservice architecture in a monorepo.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Services](#services)
  - [Customer Service](#customer-service)
  - [Driver Service](#driver-service)
  - [Ride Service](#ride-service)
  - [Payment Service](#payment-service)
- [Mobile Applications](#mobile-applications)
  - [Customer Mobile App](#customer-mobile-app)
  - [Driver Mobile App](#driver-mobile-app)
- [Common Libraries](#common-libraries)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally](#running-locally)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This repository is a monorepo for the Taxi Application, which includes both backend services and mobile applications for customers and drivers. The backend is implemented using a microservice architecture to ensure scalability, flexibility, and ease of maintenance.

## Services

### Customer Service

Handles all customer-related operations such as signup, login, requesting a ride, and viewing ride history.

### Driver Service

Manages driver operations including driver signup, login, accepting rides, and tracking ride status.

### Ride Service

Responsible for handling ride requests, matching drivers with customers, and tracking ride details.

### Payment Service

Processes payments, manages customer and driver accounts, and handles transactions.

## Common Libraries

The `common/` directory contains shared code such as data models, utility functions, and configuration files that are used across multiple services.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.8+ installed.
- Node.js and npm installed (if you plan to work on the front-end as well).
- An IDE or code editor such as Visual Studio Code.