import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import FloatingShapes from "@/components/FloatingShapes";
import ChatMessage from "@/components/ChatMessage";
import WelcomeScreen from "@/components/WelcomeScreen";
import TopicSidebar from "@/components/TopicSidebar";
import { queryPodcast, Source } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { enhanceQueryWithTopic, getTopicById } from "@/config/topics";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
  sources?: Source[];
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [activeTopic, setActiveTopic] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      // Enhance query with topic context if a topic is active
      const enhancedQuery = enhanceQueryWithTopic(inputValue, activeTopic);
      
      // Call the actual RAG API with enhanced query
      const response = await queryPodcast(enhancedQuery, 3);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        sender: "ai",
        timestamp: new Date(),
        sources: response.sources, // Always include source
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    } catch (error) {
      console.error('Query failed:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I couldn't process your request. The backend might be offline. Please check if the API is running at http://localhost:8000",
        sender: "ai",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false);
      
      toast({
        title: "Connection Error",
        description: "Could not connect to the backend API",
        variant: "destructive",
      });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleTopicSelect = (topicId: string | null) => {
    setActiveTopic(topicId);
  };

  const handleSeedQuestionClick = (question: string) => {
    setInputValue(question);
    // Focus the input field
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setActiveTopic(null); // Clear topic when starting new chat
  };

  const activeTopicObject = activeTopic ? getTopicById(activeTopic) : null;

  return (
    <div className="relative h-screen flex flex-col overflow-hidden">
      <FloatingShapes />
      
      {/* Header */}
      <header className="relative z-10 border-b-4 border-foreground bg-background/80 backdrop-blur-sm flex-shrink-0">
        <div className="w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center border-2 border-foreground shadow-[0_4px_0_0_hsl(0_0%_10%)]">
              <Sparkles className="w-6 h-6 text-background" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-display font-black tracking-tight">
                WTF Podcast Chat
              </h1>
              {activeTopicObject && (
                <Badge 
                  variant="secondary" 
                  className="mt-1 border border-foreground/20 font-semibold text-xs"
                >
                  {activeTopicObject.icon} {activeTopicObject.name}
                </Badge>
              )}
            </div>
          </div>
          <Button 
            variant="outline" 
            className="border-2 border-foreground font-bold shadow-[0_4px_0_0_hsl(0_0%_10%)] hover:translate-y-0.5 hover:shadow-[0_2px_0_0_hsl(0_0%_10%)] transition-all"
            onClick={handleNewChat}
          >
            New Chat
          </Button>
        </div>
      </header>

      {/* Main Content Area with Sidebar */}
      <div className="flex-1 relative z-10 flex overflow-hidden">
        {/* Topic Sidebar - Scrollable */}
        <TopicSidebar
          activeTopic={activeTopic}
          onTopicSelect={handleTopicSelect}
          onSeedQuestionClick={handleSeedQuestionClick}
        />

        {/* Chat Area - Centered and Fixed Width */}
        <div className="flex-1 flex items-center justify-center overflow-hidden">
          <div className="w-full max-w-4xl h-full flex flex-col py-6 px-4">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <WelcomeScreen />
          </div>
        ) : (
          <ScrollArea ref={scrollAreaRef} className="flex-1 pr-4">
            <div className="space-y-6 pb-4">
              {messages.map((message) => (
                <div key={message.id}>
                  <ChatMessage message={message} />
                  
                  {/* Display primary source - simplified and clean */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="ml-14 mt-3">
                      {message.sources.slice(0, 1).map((source, idx) => (
                        <a
                          key={idx}
                          href={source.youtube_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors group"
                        >
                          <span className="opacity-60">💬</span>
                          <span className="font-medium">{source.guest}</span>
                          <span className="opacity-60">•</span>
                          <span className="opacity-80">{source.guest_expertise}</span>
                          <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-60 transition-opacity" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-3 slide-up">
                  <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center border-2 border-foreground flex-shrink-0">
                    <Sparkles className="w-5 h-5 text-background" />
                  </div>
                  <div className="chat-bubble-ai max-w-[80%]">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                      <div className="w-2 h-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                      <div className="w-2 h-2 bg-foreground rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        )}

        {/* Input Area */}
        <div className="mt-4 flex-shrink-0">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about podcast episodes..."
                className="pr-12 h-14 text-base border-2 border-foreground rounded-2xl shadow-[0_4px_0_0_hsl(0_0%_10%)] focus:shadow-[0_4px_0_0_hsl(332_82%_52%)] transition-all resize-none"
                disabled={isTyping}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="h-14 px-6 bg-gradient-to-r from-primary to-secondary border-2 border-foreground font-bold shadow-[0_4px_0_0_hsl(0_0%_10%)] hover:translate-y-0.5 hover:shadow-[0_2px_0_0_hsl(0_0%_10%)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
