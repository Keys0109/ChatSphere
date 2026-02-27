# ChatSphere

<<<<<<< HEAD


## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/anayanay433/chatsphere.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.com/anayanay433/chatsphere/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
=======
ChatSphere is a modern, real-time chat application built with a robust FastAPI backend and a responsive React frontend. It offers seamless messaging, user presence tracking, and a sleek user interface.

## 🚀 Features

- **Real-time Messaging**: Instant message delivery using Socket.IO.
- **User Authentication**: Secure sign-up and login with JWT-based authentication.
- **Presence System**: Real-time online/offline status updates.
- **Typing Indicators**: See when other users are typing.
- **Message History**: Persistent chat history stored in MongoDB.
- **Responsive Design**: customized CSS for a premium look and feel on desktop and mobile.
- **Rate Limiting**: API protection using SlowAPI.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Real-time**: [Socket.IO](https://python-socketio.readthedocs.io/)
- **Database**: [MongoDB](https://www.mongodb.com/) (via Motor async driver)
- **Caching/PubSub**: [Redis](https://redis.io/)
- **Authentication**: JWT (JSON Web Tokens) with `python-jose`
- **Rate Limiting**: SlowAPI

### Frontend
- **Framework**: [React](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: Custom CSS with CSS Variables
- **HTTP Client**: Axios
- **Socket Client**: socket.io-client

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python** (v3.13+)
- **Node.js** (v18+) & npm
- **MongoDB** (Local or Atlas)
- **Redis** (Local or Cloud)

## 🏁 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ChatSphere
```

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -e .
```

Configure Environment Variables:
Create a `.env` file in the `backend` directory (copy from `.env.example`):
```bash
cp .env.example .env
```
Update `.env` with your credentials:
```ini
ENVIRONMENT=development
DEBUG=true
API_VERSION=v1

# Database
MONGO_URI=mongodb://localhost:27017
MONGODB_NAME=chatsphere
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
JWT_SECRET_KEY=your_super_secret_key_change_this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run the Backend Server:
```bash
python main.py
```
The API will be available at `http://localhost:8000` (Docs at `/docs`).

### 3. Frontend Setup

Navigate to the frontend directory:
```bash
cd ../frontend
```

Install dependencies:
```bash
npm install
```

Configure Environment Variables:
Create `src/api/config.js` or similar if needed, or ensure the frontend points to `http://localhost:8000`. 
*Note: Check `src/api` or `vite.config.js` for proxy settings if applicable.*

Run the Development Server:
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173` (default Vite port).

## 📂 Project Structure

```
ChatSphere/
├── backend/
│   ├── app/
│   │   ├── models/       # Pydantic models & DB schemas
│   │   ├── routes/       # API endpoints (Auth, Users, Chats)
│   │   ├── services/     # Business logic & DB interactions
│   │   ├── utils/        # Helper functions
│   │   ├── config.py     # Configuration settings
│   │   ├── database.py   # DB connection logic
│   │   └── sio.py        # Socket.IO event handlers
│   ├── main.py           # Application entry point
│   ├── pyproject.toml    # Python dependencies
│   └── .env.example      # Environment variables template
│
└── frontend/
    ├── src/
    │   ├── components/   # Reusable UI components
    │   ├── context/      # React Context (Auth, Global State)
    │   ├── pages/        # Application pages (Login, Chat)
    │   ├── socket/       # Socket.IO client logic
    │   └── index.css     # Global styles
    ├── index.html        # Entry HTML
    └── vite.config.js    # Vite configuration
```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License.
>>>>>>> d1a496a (all changes)
