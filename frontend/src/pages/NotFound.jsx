import { Compass } from "lucide-react";
import { Button, Card, Empty, Page } from "@/components/ui";
export default function NotFound() {
  return <Page><Card><Empty icon={Compass} title="Page not found" text="That page doesn't exist or was moved." action={<Button to="/dashboard" size="sm">Go to dashboard</Button>} /></Card></Page>;
}
