import { Topic } from "@/config/topics";
import { Card } from "@/components/ui/card";
import { Check } from "lucide-react";

interface TopicCardProps {
  topic: Topic;
  isActive: boolean;
  onSelect: () => void;
  onSeedQuestionClick: (question: string) => void;
}

const TopicCard = ({ topic, isActive, onSelect, onSeedQuestionClick }: TopicCardProps) => {
  return (
    <Card
      className={`
        p-4 cursor-pointer transition-all duration-200
        border-2 border-foreground
        hover:shadow-[0_6px_0_0_hsl(0_0%_10%)]
        hover:translate-y-[-2px]
        ${isActive 
          ? 'shadow-[0_6px_0_0_hsl(332_82%_52%)] border-primary bg-primary/5' 
          : 'shadow-[0_4px_0_0_hsl(0_0%_10%)]'
        }
      `}
      onClick={onSelect}
    >
      {/* Header with icon and title */}
      <div className="flex items-start gap-3 mb-2">
        <div className="text-3xl flex-shrink-0">{topic.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-sm leading-tight">{topic.name}</h3>
            {isActive && (
              <Check className="w-4 h-4 text-primary flex-shrink-0" />
            )}
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
        {topic.description}
      </p>

      {/* Seed Questions */}
      <div className="space-y-1.5">
        <p className="text-xs font-semibold text-foreground/60 mb-2">Try asking:</p>
        {topic.seedQuestions.map((question, idx) => (
          <button
            key={idx}
            onClick={(e) => {
              e.stopPropagation();
              onSeedQuestionClick(question);
            }}
            className="
              w-full text-left text-xs px-2 py-1.5 rounded
              bg-background/50 hover:bg-accent
              border border-foreground/10
              transition-colors
              flex items-start gap-1.5
            "
          >
            <span className="opacity-60 flex-shrink-0">💬</span>
            <span className="leading-snug">{question}</span>
          </button>
        ))}
      </div>
    </Card>
  );
};

export default TopicCard;

