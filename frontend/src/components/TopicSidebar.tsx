import { useState } from "react";
import { ChevronLeft, ChevronRight, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import TopicCard from "@/components/TopicCard";
import { TOPICS, Topic } from "@/config/topics";

interface TopicSidebarProps {
  activeTopic: string | null;
  onTopicSelect: (topicId: string | null) => void;
  onSeedQuestionClick: (question: string) => void;
}

const TopicSidebar = ({ activeTopic, onTopicSelect, onSeedQuestionClick }: TopicSidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleTopicClick = (topicId: string) => {
    // Toggle: if already active, deactivate; otherwise activate
    if (activeTopic === topicId) {
      onTopicSelect(null);
    } else {
      onTopicSelect(topicId);
    }
  };

  return (
    <aside
      className={`
        relative border-r-4 border-foreground bg-background/80 backdrop-blur-sm
        transition-all duration-300 ease-in-out flex-shrink-0
        ${isCollapsed ? 'w-16' : 'w-80'}
      `}
    >
      {/* Collapse/Expand Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="
          absolute -right-3 top-4 z-10
          w-6 h-6 rounded-full
          bg-background border-2 border-foreground
          shadow-[0_2px_0_0_hsl(0_0%_10%)]
          hover:shadow-[0_4px_0_0_hsl(0_0%_10%)]
          hover:translate-y-[-2px]
          transition-all
          flex items-center justify-center
        "
      >
        {isCollapsed ? (
          <ChevronRight className="w-3 h-3" />
        ) : (
          <ChevronLeft className="w-3 h-3" />
        )}
      </button>

      {isCollapsed ? (
        /* Collapsed View - Just Icons */
        <div className="flex flex-col items-center gap-4 py-6">
          {TOPICS.map((topic) => (
            <button
              key={topic.id}
              onClick={() => {
                handleTopicClick(topic.id);
                setIsCollapsed(false); // Auto-expand when selecting
              }}
              className={`
                text-2xl w-12 h-12 rounded-lg
                border-2 border-foreground
                flex items-center justify-center
                transition-all
                hover:shadow-[0_4px_0_0_hsl(0_0%_10%)]
                hover:translate-y-[-2px]
                ${activeTopic === topic.id 
                  ? 'bg-primary/10 shadow-[0_4px_0_0_hsl(332_82%_52%)]' 
                  : 'bg-background shadow-[0_2px_0_0_hsl(0_0%_10%)]'
                }
              `}
              title={topic.name}
            >
              {topic.icon}
            </button>
          ))}
        </div>
      ) : (
        /* Expanded View - Full Cards */
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b-2 border-foreground">
            <h2 className="font-display font-bold text-lg">Conversation Topics</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Select a topic to focus your questions
            </p>
          </div>

          {/* Topics List */}
          <ScrollArea className="flex-1 px-4 py-4">
            <div className="space-y-3">
              {TOPICS.map((topic) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  isActive={activeTopic === topic.id}
                  onSelect={() => handleTopicClick(topic.id)}
                  onSeedQuestionClick={onSeedQuestionClick}
                />
              ))}
            </div>
          </ScrollArea>

          {/* Clear Topic Button (if active) */}
          {activeTopic && (
            <div className="p-4 border-t-2 border-foreground">
              <Button
                onClick={() => onTopicSelect(null)}
                variant="outline"
                className="
                  w-full border-2 border-foreground font-bold
                  shadow-[0_4px_0_0_hsl(0_0%_10%)]
                  hover:translate-y-0.5
                  hover:shadow-[0_2px_0_0_hsl(0_0%_10%)]
                  transition-all
                "
              >
                <X className="w-4 h-4 mr-2" />
                Clear Topic Filter
              </Button>
            </div>
          )}
        </div>
      )}
    </aside>
  );
};

export default TopicSidebar;

