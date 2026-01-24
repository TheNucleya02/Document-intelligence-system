import { Link } from "react-router-dom";
import { ArrowRight, FileText, MessageSquare, Zap, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold">D</span>
            </div>
            <span className="font-semibold">Document Intelligence</span>
          </div>
          <Link to="/dashboard">
            <Button>
              Go to Dashboard
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6 max-w-3xl mx-auto">
          Intelligent Document Analysis & Q&A
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Upload your documents and get instant answers. Our RAG-powered system analyzes
          your files and enables natural language conversations with your data.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link to="/dashboard">
            <Button size="lg">
              Get Started
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
          <Button variant="outline" size="lg">
            Learn More
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16 border-t">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={FileText}
            title="Document Management"
            description="Upload, organize, and manage your documents with ease. Support for PDF, Word, and text files."
          />
          <FeatureCard
            icon={Zap}
            title="Instant Analysis"
            description="Automatic document processing and indexing. Get your documents ready for Q&A in seconds."
          />
          <FeatureCard
            icon={MessageSquare}
            title="Natural Language Q&A"
            description="Ask questions in plain English. Get accurate answers with source citations."
          />
          <FeatureCard
            icon={Shield}
            title="Enterprise Ready"
            description="Built for production with proper error handling, type safety, and scalable architecture."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Document Intelligence System • Built for Enterprise</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
