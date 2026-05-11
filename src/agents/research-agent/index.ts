import { Logger } from '../../utils/config.js';
import WebSocket from 'ws';

export class DeepResearchAgent {
  private logger: Logger;
  private backendUrl: string;

  constructor() {
    this.logger = new Logger('DeepResearchAgent');
    // Default to the websocket endpoint format
    this.backendUrl = process.env.RESEARCHER_BACKEND_URL || 'ws://localhost:8000/ws';
  }

  async conductResearch(query: string): Promise<string> {
    this.logger.log(`Starting deep research for query: ${query}`);
    return new Promise((resolve, reject) => {
      this.logger.log(`Connecting to GPT-Researcher backend at ${this.backendUrl}...`);
      
      const ws = new WebSocket(this.backendUrl);

      ws.on('open', () => {
        this.logger.log('Connected to backend, initiating task...');
        // gpt-researcher expects a special "start JSON" format on the websocket
        const requestData = {
          task: `${query} (必须全篇使用中文撰写报告，包括所有小标题和正文)`,
          report_type: 'research_report',
          report_source: 'web',
          tone: 'Objective',
          agent: 'Auto Agent',
        };
        ws.send(`start ${JSON.stringify(requestData)}`);
      });

      ws.on('message', (data: Buffer) => {
        try {
          const msg = JSON.parse(data.toString());
          if (msg.type === 'report') {
            this.logger.log("Research report received.");
            ws.close();
            resolve(msg.output);
          } else if (msg.type === 'logs') {
            // Optional: Print progress logs from backend
            this.logger.log(`[Backend Log] ${msg.output}`);
          }
        } catch (e) {
            // Ignore non-json or unparseable messages
        }
      });

      ws.on('error', (error) => {
        this.logger.error('WebSocket Error:', error instanceof Error ? error : new Error(String(error)));
        reject(new Error(`Research failing: Is the docker-compose backend running at ${this.backendUrl}?`));
      });

      ws.on('close', () => {
        // If it closes before resolving, reject
        reject(new Error('WebSocket closed before receiving final report.'));
      });
    });
  }
}
