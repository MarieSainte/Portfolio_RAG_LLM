export type Domain = 'ml' | 'mlops' | 'dlrl' | 'genai' | 'pilot';

export interface ProjectLink {
  label: string;
  url: string;
}

export interface ProjectNodeData {
  id: string;
  icon: string;
  domain: Domain;
  stack: string[];
  hasFact: boolean;
  links?: ProjectLink[];
}

export const DOMAIN_IDS: Domain[] = ['ml', 'mlops', 'dlrl', 'genai', 'pilot'];

export const DOMAIN_COLORS: Record<Domain, string> = {
  ml: '#5b9bf8',
  mlops: '#34c98e',
  dlrl: '#a678f2',
  genai: '#f59e0b',
  pilot: '#8d8a86',
};

export const PROJECT_NODES: ProjectNodeData[] = [
  {
    id: 'P1',
    icon: '🧭',
    domain: 'pilot',
    hasFact: true,
    stack: ['Organisation', 'Planning', 'Collaboration mentor'],
  },
  {
    id: 'P2',
    icon: '👗',
    domain: 'ml',
    hasFact: false,
    stack: ['Python', 'Hugging Face', 'Modèle pré-entraîné', 'Notebooks'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/fashion-trend-ai' }],
  },
  {
    id: 'P3',
    icon: '🏢',
    domain: 'ml',
    hasFact: false,
    stack: ['Python', 'scikit-learn', 'pandas', 'Régression', 'Poetry'],
  },
  {
    id: 'P4',
    icon: '📊',
    domain: 'ml',
    hasFact: false,
    stack: ['scikit-learn', 'SMOTE', 'Pipelines', 'Interprétabilité'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/detection-attrition' }],
  },
  {
    id: 'P5',
    icon: '🚀',
    domain: 'mlops',
    hasFact: true,
    stack: ['FastAPI', 'PostgreSQL', 'Pytest', 'GitHub Actions', 'Docker', 'HF Spaces'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/futurisys_project' }],
  },
  {
    id: 'P6',
    icon: '🏦',
    domain: 'mlops',
    hasFact: true,
    stack: ['XGBoost', 'Optuna', 'MLflow'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/credit_score' }],
  },
  {
    id: 'P7',
    icon: '💬',
    domain: 'genai',
    hasFact: false,
    stack: ['LangChain', 'FAISS', 'Mistral AI', 'Ragas', 'Gradio', 'FastAPI'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/puls-events-chatbot' }],
  },
  {
    id: 'P8',
    icon: '🛡️',
    domain: 'mlops',
    hasFact: true,
    stack: ['FastAPI', 'Streamlit', 'Prometheus', 'Grafana', 'Evidently', 'GCP'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/credit_score' }],
  },
  {
    id: 'P9',
    icon: '📋',
    domain: 'pilot',
    hasFact: false,
    stack: ['Gestion de projet', 'Analyse de risques', 'Prototypage'],
  },
  {
    id: 'P10',
    icon: '🧠',
    domain: 'dlrl',
    hasFact: true,
    stack: ['CNN', 'ResNet50', 'KMeans', 'Transfer learning'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/brain-scan-ai' }],
  },
  {
    id: 'P11',
    icon: '🎮',
    domain: 'dlrl',
    hasFact: false,
    stack: ['Stable-Baselines3', 'DQN', 'Gymnasium', 'TensorBoard', 'FastAPI'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/bot-lunaire-eagle' }],
  },
  {
    id: 'P12',
    icon: '📰',
    domain: 'mlops',
    hasFact: false,
    stack: ['Airflow', 'PostgreSQL', 'ETL', 'Streamlit', 'Docker Compose'],
  },
  {
    id: 'P13',
    icon: '♟️',
    domain: 'genai',
    hasFact: true,
    stack: ['LangGraph', 'Milvus', 'Stockfish', 'Lichess API', 'Angular', 'MongoDB'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/ffe-ai' }],
  },
  {
    id: 'P14',
    icon: '🩺',
    domain: 'genai',
    hasFact: true,
    stack: ['Qwen3-1.7B', 'Unsloth · TRL', 'LoRA · DPO', 'Presidio', 'DSPy', 'vLLM', 'GCP GPU'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/triage-medical-chatbot' }],
  },
  {
    id: 'P15',
    icon: '🌐',
    domain: 'genai',
    hasFact: true,
    stack: ['Angular', 'FastAPI', 'ChromaDB', 'sentence-transformers', 'Mistral AI'],
    links: [{ label: 'GitHub', url: 'https://github.com/MarieSainte/Portfolio_RAG_LLM' }],
  },
];
