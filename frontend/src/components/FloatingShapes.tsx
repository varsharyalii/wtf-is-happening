const FloatingShapes = () => {
  return (
    <>
      {/* Decorative floating shapes */}
      <div className="floating-shape top-20 left-10 w-16 h-16 bg-primary rounded-full" style={{ animationDelay: "0s" }}></div>
      <div className="floating-shape top-40 right-20 w-12 h-12 bg-secondary rotate-45" style={{ animationDelay: "1s" }}></div>
      <div className="floating-shape bottom-32 left-1/4 w-20 h-20 bg-accent rounded-full" style={{ animationDelay: "2s" }}></div>
      <div className="floating-shape top-1/3 right-1/3 w-8 h-8 bg-primary rotate-12" style={{ animationDelay: "1.5s" }}></div>
      <div className="floating-shape bottom-20 right-10 w-14 h-14 bg-secondary rounded-full" style={{ animationDelay: "0.5s" }}></div>
      
      {/* Cloud-like shapes */}
      <svg className="floating-shape top-10 right-1/4 w-24 h-16" style={{ animationDelay: "0.8s" }} viewBox="0 0 100 60" fill="none">
        <path d="M20 40 Q10 40 10 30 Q10 20 20 20 Q20 10 35 10 Q50 10 50 20 Q65 20 65 30 Q65 40 55 40 Z" fill="currentColor" className="text-muted-foreground" stroke="currentColor" strokeWidth="2"/>
      </svg>
      
      <svg className="floating-shape bottom-1/3 left-1/3 w-20 h-14" style={{ animationDelay: "2.3s" }} viewBox="0 0 100 60" fill="none">
        <path d="M20 40 Q10 40 10 30 Q10 20 20 20 Q20 10 35 10 Q50 10 50 20 Q65 20 65 30 Q65 40 55 40 Z" fill="currentColor" className="text-muted-foreground" stroke="currentColor" strokeWidth="2"/>
      </svg>

      {/* Star shapes */}
      <svg className="floating-shape top-1/4 left-1/2 w-10 h-10" style={{ animationDelay: "1.2s" }} viewBox="0 0 24 24" fill="none">
        <path d="M12 2L15 9L22 9L16.5 14L19 21L12 16.5L5 21L7.5 14L2 9L9 9L12 2Z" fill="currentColor" className="text-accent" stroke="currentColor" strokeWidth="1.5"/>
      </svg>
    </>
  );
};

export default FloatingShapes;
