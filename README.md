<div align="center">

  <img src="assets/profile-header.svg" alt="RCZ88 | Algorithms, systems programming, neural networks" width="100%" />

  <p><strong>Algorithms &nbsp;·&nbsp; Systems Programming &nbsp;·&nbsp; Neural Networks</strong></p>
  <p>I like understanding what happens beneath the abstractions, then building things with that understanding.</p>

  <p>
    <a href="#featured-work">FEATURED WORK</a> &nbsp;·&nbsp;
    <a href="#engineering-activity">ENGINEERING ACTIVITY</a> &nbsp;·&nbsp;
    <a href="https://github.com/RCZ88?tab=repositories">ALL REPOSITORIES</a>
  </p>

  <p>
    <a href="mailto:clementzhao74@gmail.com"><img src="https://img.shields.io/badge/Email-Contact-94a3b8?style=flat-square&logo=gmail&logoColor=white" alt="Email"/></a>
    <a href="https://instagram.com/devwithcz"><img src="https://img.shields.io/badge/Instagram-Profile-c084fc?style=flat-square&logo=instagram&logoColor=white" alt="Instagram"/></a>
    <a href="https://www.threads.net/@rclement_z"><img src="https://img.shields.io/badge/Threads-%40rclement_z-000000?style=flat-square&logo=threads&logoColor=white" alt="Threads"/></a>
  </p>
</div>

---

## What I'm exploring

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>01 / Algorithms & data structures</h3>
      Understanding time and space complexity, implementing data structures, and learning why an algorithm works instead of only memorising a solution.
    </td>
    <td width="50%" valign="top">
      <h3>02 / C & memory</h3>
      Pointers, allocation, ownership, resizing, failure handling, and designing useful abstractions without hiding the underlying mechanics.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>03 / Neural networks</h3>
      Returning to the maths behind learning systems: forward propagation, backpropagation, attention, and small models I can reason about from first principles.
    </td>
    <td width="50%" valign="top">
      <h3>04 / AI infrastructure</h3>
      MCP servers, agent skills, context management, tool workflows, and ways to test AI-driven systems instead of trusting them blindly.
    </td>
  </tr>
</table>

<a id="featured-work"></a>

## Featured work

These projects show the problems I'm interested in, from implementing algorithms to building the infrastructure around AI-powered applications.

<table>
  <tr>
    <td width="50%" valign="top">
      <p><a href="https://github.com/RCZ88/SVMxRF-BC"><img src="https://img.shields.io/badge/PROJECT_01-ALGORITHMS-38bdf8?style=flat-square" alt="Algorithms project"/></a></p>
      <h3><a href="https://github.com/RCZ88/SVMxRF-BC">SVM vs. Random Forest</a></h3>
      <p>A from-scratch comparison on the Wisconsin Breast Cancer dataset. The goal was to understand the algorithms, not just call a prebuilt estimator.</p>
      <p><code>Python</code> <code>NumPy</code> <code>Optimisation</code></p>
      <details>
        <summary>Technical details</summary>
        <ul>
          <li>Custom SVM using the dual formulation and a quadratic-programming solver.</li>
          <li>Random Forest with recursive tree splitting, Gini impurity, bootstrapping, and feature subsampling.</li>
          <li>Stratified cross-validation and evaluation with precision, recall, and F1.</li>
        </ul>
      </details>
    </td>
    <td width="50%" valign="top">
      <p><img src="https://img.shields.io/badge/PROJECT_02-IN_DEVELOPMENT-fbbf24?style=flat-square" alt="In development"/></p>
      <h3>SALOK / Smart Memory Allocation</h3>
      <p>An experimental C library that grew out of a dynamic-array problem in a Blackjack project. I'm using it to explore memory management and reusable data structures, while the API and architecture are still being shaped by the problems I encounter.</p>
      <p><code>C</code> <code>Allocation</code> <code>Dynamic arrays</code></p>
      <details>
        <summary>What I'm working through</summary>
        <ul>
          <li>Clear ownership and allocation lifetime rules.</li>
          <li>Safe resizing and allocation-failure behaviour.</li>
          <li>Typed interfaces versus a generic internal implementation.</li>
          <li>Keeping allocation tracking separate from containers unless combining them has a clear benefit.</li>
        </ul>
        <p><em>SALOK is unfinished and not presented as a released library. Its current development work is not yet published as a finished implementation.</em></p>
      </details>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p><a href="https://github.com/RCZ88/neuroquant"><img src="https://img.shields.io/badge/PROJECT_03-MACHINE_LEARNING-a78bfa?style=flat-square" alt="Machine learning project"/></a></p>
      <h3><a href="https://github.com/RCZ88/neuroquant">NeuroQuant</a></h3>
      <p>An experimental quantitative modelling project exploring how model outputs and market signals can be combined under uncertainty.</p>
      <p><code>Python</code> <code>LSTM</code> <code>Attention</code></p>
      <details>
        <summary>Technical direction</summary>
        <p>The repository describes LSTM-based prediction, attention, sentiment analysis, Bayesian signal fusion, and market-regime detection. These are project design claims, not a guarantee that every part is fully realised in the current version.</p>
      </details>
    </td>
    <td width="50%" valign="top">
      <p><a href="https://github.com/RCZ88/RHEO"><img src="https://img.shields.io/badge/PROJECT_04-DESKTOP_SYSTEMS-5eead4?style=flat-square" alt="Desktop systems project"/></a></p>
      <h3><a href="https://github.com/RCZ88/RHEO">RHEO</a></h3>
      <p>A large desktop application exploring local activity tracking, persistent state, terminal workflows, and AI-agent orchestration.</p>
      <p><code>Electron</code> <code>React</code> <code>TypeScript</code> <code>SQLite</code></p>
      <details>
        <summary>Engineering focus</summary>
        <p>Connecting desktop UI, local data, terminal sessions, and agent workflows into an application with multiple interacting subsystems.</p>
      </details>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p><a href="https://github.com/RCZ88/mcp-ai-bridge"><img src="https://img.shields.io/badge/PROJECT_05-AI_INFRASTRUCTURE-f59e0b?style=flat-square" alt="AI infrastructure project"/></a></p>
      <h3><a href="https://github.com/RCZ88/mcp-ai-bridge">MCP-AI Bridge</a></h3>
      <p>A service for connecting AI agents to external tools through the Model Context Protocol, with request-scoped sessions and server-side credential handling.</p>
      <p><code>Python</code> <code>FastAPI</code> <code>MCP</code></p>
    </td>
    <td width="50%" valign="top">
      <p><a href="https://github.com/RCZ88/ecosystem"><img src="https://img.shields.io/badge/PROJECT_06-AGENT_WORKFLOWS-f472b6?style=flat-square" alt="Agent workflows project"/></a></p>
      <h3><a href="https://github.com/RCZ88/ecosystem">Agent ecosystem</a></h3>
      <p>A file-based approach to coordinating agent state, reusable skills, context, and structured actions without introducing a large runtime.</p>
      <p><code>JavaScript</code> <code>Automation</code> <code>Context design</code></p>
    </td>
  </tr>
</table>

## Tools, apps & environments I use

<p>
  <img src="https://img.shields.io/badge/C-00599C?style=flat-square&logo=c&logoColor=white" alt="C"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=222222" alt="JavaScript"/>
  <img src="https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white" alt="Electron"/>
  <img src="https://img.shields.io/badge/React-149ECA?style=flat-square&logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white" alt="Node.js"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel"/>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase"/>
  <img src="https://img.shields.io/badge/Cloudinary-3448C5?style=flat-square&logo=cloudinary&logoColor=white" alt="Cloudinary"/>
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black" alt="Firebase"/>
  <img src="https://img.shields.io/badge/Claude_Code-FF5E5B?style=flat-square" alt="Claude Code"/>
  <img src="https://img.shields.io/badge/OpenCode-2E8B57?style=flat-square" alt="OpenCode"/>
  <img src="https://img.shields.io/badge/Qwen_Code-5B8DEF?style=flat-square" alt="Qwen Code"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white" alt="Git"/>
  <img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=222222" alt="Linux"/>
</p>

<a id="engineering-activity"></a>

## Engineering activity

<div align="center">
  <img src="assets/commit-activity.svg" alt="Commit history and code-change statistics for public repositories" width="100%"/>
</div>

<sub>Activity covers commits attributed to @RCZ88 in public repositories owned by @RCZ88, excluding this profile repository. The chart separates the 365-day commit history from code-change statistics, and the underlying project activity is not a complete representation of every experiment or private contribution.</sub>

---

<div align="center">
  <sub>Still learning the fundamentals. Still building things that use them.</sub>
</div>
