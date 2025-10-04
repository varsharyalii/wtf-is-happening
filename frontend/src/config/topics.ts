/**
 * Topic Clusters for Guided Conversations
 * 
 * Each topic provides context for scoped RAG queries without backend filtering.
 * The contextPrompt is prepended to user queries to guide semantic search.
 */

export interface Topic {
  id: string;
  name: string;
  icon: string;
  description: string;
  contextPrompt: string;
  seedQuestions: string[];
}

export const TOPICS: Topic[] = [
  {
    id: "ai-silicon-valley",
    name: "AI Disruption & Silicon Valley Insights",
    icon: "🤖",
    description: "Explore AI innovation with leaders from OpenAI, Meta, and YouTube",
    contextPrompt: "In the context of AI disruption, innovation, and Silicon Valley insights",
    seedQuestions: [
      "What did Sam Altman say about AI safety and AGI?",
      "How does Yann LeCun view the future of AI research?",
      "What are the biggest challenges in AI product development?"
    ]
  },
  {
    id: "startup-funding",
    name: "Startup Funding & Indian Entrepreneurship",
    icon: "🚀",
    description: "Learn about building startups, fundraising, and the Indian market",
    contextPrompt: "Regarding startup ecosystems, fundraising strategies, and Indian entrepreneurship",
    seedQuestions: [
      "How do I launch my startup right now if I'm a 25 year old?",
      "What advice do successful founders give about fundraising?",
      "What are the key challenges for scaling startups globally?"
    ]
  },
  {
    id: "ethical-ai",
    name: "Ethical AI Discussions",
    icon: "⚖️",
    description: "Deep dive into AI ethics, safety, regulation, and societal impact",
    contextPrompt: "Focusing on AI ethics, safety concerns, responsible development, and societal impact",
    seedQuestions: [
      "What are the main ethical concerns around AI development?",
      "How should we think about AI regulation and governance?",
      "What role does AI play in addressing global challenges?"
    ]
  },
  {
    id: "future-vision",
    name: "Futuristic Vision of the World",
    icon: "🔮",
    description: "Visionaries discuss the next decade of technology and society",
    contextPrompt: "About future trends, technological transformation, and long-term vision for the next decade",
    seedQuestions: [
      "What does the future of work look like in an AI-driven world?",
      "How will technology transform industries in the next 10 years?",
      "What are the most exciting breakthroughs on the horizon?"
    ]
  }
];

/**
 * Get a topic by ID
 */
export function getTopicById(id: string): Topic | undefined {
  return TOPICS.find(topic => topic.id === id);
}

/**
 * Enhance a user query with topic context
 */
export function enhanceQueryWithTopic(query: string, topicId: string | null): string {
  if (!topicId) return query;
  
  const topic = getTopicById(topicId);
  if (!topic) return query;
  
  return `${topic.contextPrompt}: ${query}`;
}

