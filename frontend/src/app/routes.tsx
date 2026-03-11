import { createBrowserRouter } from 'react-router-dom';
import { Layout } from './components/Layout';
import { PlayerScoutingTool } from './pages/PlayerScoutingTool';
import { TacticalAnalysisTool } from './pages/TacticalAnalysisTool';
import { Settings } from './pages/Settings';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: Layout,
    children: [
      { index: true, Component: PlayerScoutingTool },
      { path: 'tactical-analysis', Component: TacticalAnalysisTool },
      { path: 'settings', Component: Settings },
    ],
  },
]);
