import { User, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.sender === "user";

  return (
    <div className={`flex gap-3 slide-up ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 border-foreground flex-shrink-0 ${
        isUser 
          ? "bg-gradient-to-br from-primary to-secondary" 
          : "bg-accent"
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-background" />
        ) : (
          <Sparkles className="w-5 h-5 text-background" />
        )}
      </div>
      <div className={`max-w-[80%] ${isUser ? "chat-bubble-user" : "chat-bubble-ai"}`}>
        {isUser ? (
          <p className="text-base leading-relaxed whitespace-pre-wrap break-words">
            {message.text}
          </p>
        ) : (
          <div className="text-base leading-relaxed prose prose-sm max-w-none prose-p:my-2 prose-p:leading-relaxed prose-strong:font-bold prose-strong:text-foreground prose-ul:my-2 prose-li:my-1">
            <ReactMarkdown>{message.text}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
