import { lazy, Suspense } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import AppLayout from "@/components/AppLayout";
import { PageSkeleton } from "@/components/ui";
import Landing from "@/pages/Landing";
import Auth from "@/pages/Auth";
import AdminLayout from "@/components/AdminLayout";
import AdminLogin from "@/pages/admin/AdminLogin";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const Practice = lazy(() => import("@/pages/Practice"));
const Problem = lazy(() => import("@/pages/Problem"));
const Analysis = lazy(() => import("@/pages/Analysis"));
const Submissions = lazy(() => import("@/pages/Submissions"));
const Learn = lazy(() => import("@/pages/Learn"));
const Topic = lazy(() => import("@/pages/Topic"));
const Quiz = lazy(() => import("@/pages/Quiz"));
const Analytics = lazy(() => import("@/pages/Analytics"));
const Tests = lazy(() => import("@/pages/Tests"));
const TestOverview = lazy(() => import("@/pages/TestOverview"));
const TestSolve = lazy(() => import("@/pages/TestSolve"));
const TestResult = lazy(() => import("@/pages/TestResult"));
const Notes = lazy(() => import("@/pages/Notes"));
const Community = lazy(() => import("@/pages/Community"));
const MentorChat = lazy(() => import("@/pages/MentorChat"));
const Notifications = lazy(() => import("@/pages/Notifications"));
const NotFound = lazy(() => import("@/pages/NotFound"));
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminLearners = lazy(() => import("@/pages/admin/AdminLearners"));
const AdminLearner = lazy(() => import("@/pages/admin/AdminLearner"));
const AdminTopicAnalytics = lazy(() => import("@/pages/admin/AdminTopicAnalytics"));
const AdminTopics = lazy(() => import("@/pages/admin/AdminTopics"));
const AdminTopicEditor = lazy(() => import("@/pages/admin/AdminTopicEditor"));
const AdminProblems = lazy(() => import("@/pages/admin/AdminProblems"));
const AdminProblemEditor = lazy(() => import("@/pages/admin/AdminProblemEditor"));
const AdminTests = lazy(() => import("@/pages/admin/AdminTests").then((m) => ({ default: m.AdminTests })));
const AdminTestNew = lazy(() => import("@/pages/admin/AdminTests").then((m) => ({ default: m.AdminTestNew })));
const AdminAnnouncements = lazy(() => import("@/pages/admin/AdminAnnouncements"));
const AdminInbox = lazy(() => import("@/pages/admin/AdminInbox"));

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  const loc = useLocation();
  if (loading) return <PageSkeleton />;
  if (!user) return <Navigate to={`/auth?next=${encodeURIComponent(loc.pathname + loc.search)}`} replace />;
  return children;
}

export default function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="learners" element={<AdminLearners />} />
          <Route path="learners/:id" element={<AdminLearner />} />
          <Route path="topic-analytics" element={<AdminTopicAnalytics />} />
          <Route path="topics" element={<AdminTopics />} />
          <Route path="topics/new" element={<AdminTopicEditor />} />
          <Route path="topics/:id" element={<AdminTopicEditor />} />
          <Route path="problems" element={<AdminProblems />} />
          <Route path="problems/new" element={<AdminProblemEditor />} />
          <Route path="problems/:id" element={<AdminProblemEditor />} />
          <Route path="tests" element={<AdminTests />} />
          <Route path="tests/new" element={<AdminTestNew />} />
          <Route path="announcements" element={<AdminAnnouncements />} />
          <Route path="inbox" element={<AdminInbox />} />
          <Route path="community" element={<Community admin />} />
          <Route path="*" element={<NotFound />} />
        </Route>
        <Route element={<RequireAuth><AppLayout /></RequireAuth>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/practice/:id" element={<Problem />} />
          <Route path="/practice/:id/analysis" element={<Analysis />} />
          <Route path="/practice/:id/submissions" element={<Submissions />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/learn/:id" element={<Topic />} />
          <Route path="/learn/:id/quiz" element={<Quiz />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/tests" element={<Tests />} />
          <Route path="/tests/:id" element={<TestOverview />} />
          <Route path="/tests/:id/solve/:index" element={<TestSolve />} />
          <Route path="/tests/:id/result" element={<TestResult />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/community" element={<Community />} />
          <Route path="/mentor" element={<MentorChat />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
