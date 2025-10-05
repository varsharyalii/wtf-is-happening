import { Sparkles, Mic, MessageCircle, Compass } from "lucide-react";

const WelcomeScreen = () => {
  const suggestions = [
    { icon: Mic, text: "Get expert advice on something", color: "bg-primary" },
    { icon: MessageCircle, text: "Debate an idea with me", color: "bg-secondary" },
    { icon: Compass, text: "Just exploring? Start here", color: "bg-accent" },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center px-4 py-12">
      <div className="mb-8 relative">
        <div className="w-24 h-24 bg-gradient-to-br from-primary via-secondary to-accent rounded-full flex items-center justify-center border-4 border-foreground shadow-[0_8px_0_0_hsl(0_0%_10%)] mb-6">
          <Sparkles className="w-12 h-12 text-background animate-pulse" />
        </div>
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-secondary rounded-full border-2 border-foreground"></div>
        <div className="absolute -bottom-1 -left-1 w-6 h-6 bg-accent rotate-45 border-2 border-foreground"></div>
      </div>

      <h1 className="text-4xl md:text-5xl font-display font-black mb-4 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
        What's up? 👋
      </h1>
      
      <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-md font-medium">
        I've binged all the WTF episodes. Let's talk!
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="group p-6 bg-card border-2 border-foreground rounded-2xl shadow-[0_6px_0_0_hsl(0_0%_10%)] hover:translate-y-1 hover:shadow-[0_4px_0_0_hsl(0_0%_10%)] transition-all duration-200"
          >
            <div className={`w-12 h-12 ${suggestion.color} rounded-full flex items-center justify-center border-2 border-foreground mx-auto mb-4 group-hover:scale-110 transition-transform`}>
              <suggestion.icon className="w-6 h-6 text-background" />
            </div>
            <p className="font-bold text-foreground">{suggestion.text}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default WelcomeScreen;
