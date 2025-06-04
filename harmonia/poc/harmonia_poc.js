/**
 * HARMONIA POC - Reflexive System with ATHENA
 * ---------------------------------------------
 * A prototype of the HARMONIA language with reflexive capabilities
 * and connection to ATHENA for self-evaluation and self-correction
 */

// System Configuration
const SYSTEM_CONFIG = {
  name: "HARMONIA-POC",
  version: "0.1.0-embryonic",
  logLevel: "debug",
  athenaEndpoint: "https://api.athena-ai.synergia/v1",
  selfReflectionInterval: 5000, // ms
};

/**
 * CellularComponent - Base class for all cellular components
 * Inspired by the cellular paradigm with membranes, gradients, and signaling
 */
class CellularComponent {
  constructor(id, type) {
    this.id = id;
    this.type = type;
    this.membrane = {};      // Defines input/output interfaces
    this.state = {           // Dynamic internal state
      health: 1.0,
      energy: 1.0,
      connections: [],
      lastReflection: null,
      metadata: {},
    };
    this.receptors = [];     // Signal entry points
    this.emitters = [];      // Signal exit points
    this.metabolism = {      // Resource management
      energyConsumption: 0.01,
      autoRegeneration: 0.005,
    };
    this.log(`${this.type} ${this.id} created`);
  }

  /**
   * Membrane - Interface defining which signals can enter and exit
   */
  defineMembrane(config) {
    this.membrane = {
      permeable: config.permeable || [],
      semipermeable: config.semipermeable || [],
      impermeable: config.impermeable || [],
      filters: config.filters || {},
    };
    return this;
  }

  /**
   * Metabolism - Energy management of the component
   */
  processMetabolism() {
    // Base energy consumption
    this.state.energy -= this.metabolism.energyConsumption;

    // Auto-regeneration
    if (this.state.energy < 0.9) {
      this.state.energy += this.metabolism.autoRegeneration;
    }

    // Check energy state
    if (this.state.energy < 0.1) {
      this.log(`ALERT: Critical energy level (${this.state.energy.toFixed(2)})`, "warn");
    }

    return this.state.energy;
  }

  /**
   * Receptor - Receives and processes an incoming signal
   */
  receive(signal, source) {
    // Check if the signal can cross the membrane
    if (!this.canReceiveSignal(signal.type)) {
      this.log(`Signal ${signal.type} rejected by membrane`, "info");
      return false;
    }

    // Apply membrane filters if defined
    let processedSignal = signal;
    if (this.membrane.filters[signal.type]) {
      processedSignal = this.membrane.filters[signal.type](signal);
    }

    // Process the signal by the appropriate receptor
    const receptor = this.receptors.find(r => r.type === signal.type);
    if (receptor) {
      receptor.process(processedSignal, source);
      this.log(`Signal ${signal.type} processed by receptor`, "debug");
    } else {
      // Default generic receptor
      this.log(`Signal ${signal.type} received without specific receptor`, "debug");
      this.state.metadata[`last_${signal.type}`] = processedSignal;
    }

    return true;
  }

  /**
   * Emitter - Sends a signal outward
   */
  emit(type, data, targets = []) {
    const signal = {
      type,
      data,
      source: {
        id: this.id,
        type: this.type,
      },
      timestamp: Date.now(),
    };

    // Send the signal to all recipients
    if (targets.length === 0) {
      // Global broadcast via message bus
      MessageBus.broadcast(signal);
      this.log(`Signal ${type} broadcast globally`, "debug");
    } else {
      // Targeted emission
      targets.forEach(target => {
        MessageBus.sendDirectly(signal, target);
      });
      this.log(`Signal ${type} sent to ${targets.length} targets`, "debug");
    }

    return signal;
  }

  /**
   * Checks if a signal type can cross the membrane
   */
  canReceiveSignal(signalType) {
    if (this.membrane.permeable.includes(signalType)) {
      return true;
    }
    if (this.membrane.impermeable.includes(signalType)) {
      return false;
    }
    if (this.membrane.semipermeable.includes(signalType)) {
      // Permeability depends on current state
      return this.state.energy > 0.3; // Example: requires minimal energy
    }
    // By default, accept unknown signals
    return true;
  }

  /**
   * Logging with context
   */
  log(message, level = "info") {
    const logLevels = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
    };

    const systemLevel = logLevels[SYSTEM_CONFIG.logLevel] || 1;
    const messageLevel = logLevels[level] || 1;

    if (messageLevel >= systemLevel) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] [${level.toUpperCase()}] [${this.type}:${this.id}] ${message}`);
    }
  }
}

/**
 * ATHENA - Artificial Intelligence interface for reflexivity
 * Allows HARMONIA to observe, evaluate, and transform its own code
 */
class AthenaInterface {
  constructor(config = {}) {
    this.endpoint = config.endpoint || SYSTEM_CONFIG.athenaEndpoint;
    this.apiKey = config.apiKey || process.env.ATHENA_API_KEY;
    this.contextMemory = [];
    this.state = {
      connected: false,
      lastConnection: null,
      pendingQueries: 0,
    };

    // Attempt initial connection
    this.connect();
  }

  /**
   * Establishes a connection with the ATHENA API
   */
  async connect() {
    try {
      // Simulated connection for POC
      console.log("[ATHENA] Initializing connection...");
      await new Promise(resolve => setTimeout(resolve, 1000));

      this.state.connected = true;
      this.state.lastConnection = new Date();
      console.log("[ATHENA] Connection established successfully");

      return true;
    } catch (error) {
      console.error("[ATHENA] Connection error:", error);
      this.state.connected = false;
      return false;
    }
  }

  /**
   * Evaluates HARMONIA code and suggests improvements
   */
  async evaluateCode(code, context = {}) {
    if (!this.state.connected) {
      await this.connect();
    }

    this.state.pendingQueries++;

    try {
      console.log("[ATHENA] Code evaluation in progress...");

      // Simulated evaluation process for POC
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create a simulated response for the prototype
      const evaluation = this.simulateCodeEvaluation(code, context);

      // Save context for interaction continuity
      this.contextMemory.push({
        timestamp: new Date(),
        code: code,
        context: context,
        evaluation: evaluation,
      });

      // Limit memory to 10 exchanges to avoid overload
      if (this.contextMemory.length > 10) {
        this.contextMemory.shift();
      }

      this.state.pendingQueries--;
      return evaluation;

    } catch (error) {
      console.error("[ATHENA] Evaluation error:", error);
      this.state.pendingQueries--;
      return {
        success: false,
        error: error.message,
        suggestions: [],
      };
    }
  }

  /**
   * Transforms HARMONIA code based on ATHENA recommendations
   */
  async transformCode(code, transformations = [], context = {}) {
    if (!this.state.connected) {
      await this.connect();
    }

    this.state.pendingQueries++;

    try {
      console.log("[ATHENA] Code transformation in progress...");

      // Simulated transformation process for POC
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulate applying transformations for the prototype
      let transformedCode = code;

      // Sequential application of transformations
      for (const transform of transformations) {
        if (transform.type === 'replace') {
          transformedCode = transformedCode.replace(
            transform.target,
            transform.replacement
          );
        } else if (transform.type === 'insert') {
          const insertPosition = transform.position === 'start'
            ? 0
            : transform.position === 'end'
              ? transformedCode.length
              : transform.position;

          transformedCode =
            transformedCode.slice(0, insertPosition) +
            transform.content +
            transformedCode.slice(insertPosition);
        }
      }

      // Analyze the result to verify improvements
      const verification = await this.evaluateCode(transformedCode, {
        ...context,
        isTransformation: true,
        originalCode: code,
      });

      this.state.pendingQueries--;

      return {
        success: true,
        originalCode: code,
        transformedCode: transformedCode,
        verification: verification,
        appliedTransformations: transformations.length,
      };

    } catch (error) {
      console.error("[ATHENA] Transformation error:", error);
      this.state.pendingQueries--;
      return {
        success: false,
        error: error.message,
        originalCode: code,
        transformedCode: code, // Unchanged in case of error
      };
    }
  }

  /**
   * Simulated evaluation function for POC
   * In a real implementation, this would be replaced by ATHENA's AI
   */
  simulateCodeEvaluation(code, context = {}) {
    // Basic analysis to simulate pattern detection
    const potentialIssues = [];

    // Search for simple patterns to improve
    if (code.includes('for (') && !code.includes('forEach')) {
      potentialIssues.push({
        type: 'suggestion',
        severity: 'minor',
        description: 'Consider using forEach for a more functional approach',
        lineNumber: code.indexOf('for ('),
        recommendation: 'Replace traditional loops with functional methods like .forEach, .map, or .reduce when appropriate'
      });
    }

    if (code.includes('console.log') && context.stage === 'production') {
      potentialIssues.push({
        type: 'warning',
        severity: 'moderate',
        description: 'console.log statements present in production',
        lineNumber: code.indexOf('console.log'),
        recommendation: 'Replace console.log with a configurable logging system based on the environment'
      });
    }

    if (!code.includes('try {') && code.includes('await ')) {
      potentialIssues.push({
        type: 'error',
        severity: 'major',
        description: 'Asynchronous operations without error handling',
        lineNumber: code.indexOf('await ''),
        recommendation: 'Wrap asynchronous operations in try/catch blocks'
      });
    }

    // Simulated structural analysis
    const bioStructureScore = Math.random() * 0.3 + 0.7; // 0.7 to 1.0
    const performanceScore = Math.random() * 0.4 + 0.6;  // 0.6 to 1.0
    const adaptabilityScore = Math.random() * 0.5 + 0.5; // 0.5 to 1.0

    return {
      success: true,
      timestamp: new Date(),
      metrics: {
        structuralBiomimicry: bioStructureScore,
        performance: performanceScore,
        adaptability: adaptabilityScore,
        overallHealth: (bioStructureScore + performanceScore + adaptabilityScore) / 3,
      },
      issues: potentialIssues,
      recommendations: [
        {
          type: 'structure',
          description: 'Increase cellular modularity',
          examples: [
            'Break down large functions into specialized cells',
            'Ensure each module has a single responsibility'
          ]
        },
        {
          type: 'pattern',
          description: 'Strengthen homeostatic mechanisms',
          examples: [
            'Add automatic energy state checks',
            'Implement negative feedback loops for stabilization'
          ]
        }
      ],
      transformations: potentialIssues.map(issue => {
        // Generate automatic transformations based on detected issues
        if (issue.type === 'suggestion' && issue.description.includes('forEach')) {
          return {
            type: 'replace',
            target: 'for (let i = 0; i < array.length; i++)',
            replacement: 'array.forEach((item, index) =>'
          };
        }
        if (issue.type === 'warning' && issue.description.includes('console.log')) {
          return {
            type: 'replace',
            target: 'console.log',
            replacement: 'this.log'
          };
        }
        return null;
      }).filter(t => t !== null)
    };
  }
}

/**
 * Message Bus for communication between HARMONIA cells
 * Implements the intercellular signaling system
 */
class MessageBus {
  static subscribers = {};
  static messageLog = [];

  /**
   * Subscribe to a message type
   */
  static subscribe(type, callback, context) {
    if (!this.subscribers[type]) {
      this.subscribers[type] = [];
    }

    this.subscribers[type].push({
      callback,
      context
    });

    console.log(`[MessageBus] New subscription to '${type}' by ${context.type}:${context.id}`);
    return true;
  }

  /**
   * Unsubscribe from a message type
   */
  static unsubscribe(type, context) {
    if (!this.subscribers[type]) return false;

    const initialCount = this.subscribers[type].length;
    this.subscribers[type] = this.subscribers[type].filter(
      sub => !(sub.context.id === context.id && sub.context.type === context.type)
    );

    const newCount = this.subscribers[type].length;
    if (newCount < initialCount) {
      console.log(`[MessageBus] Unsubscribed from '${type}' by ${context.type}:${context.id}`);
      return true;
    }

    return false;
  }

  /**
   * Broadcast a message to all subscribers of the type
   */
  static broadcast(signal) {
    const { type } = signal;

    if (!this.subscribers[type]) {
      console.log(`[MessageBus] No subscribers for type '${type}'`);
      return 0;
    }

    // Log the message for audit and reflexivity
    this.logMessage(signal);

    // Send to subscribers
    let deliveryCount = 0;
    this.subscribers[type].forEach(sub => {
      try {
        if (sub.context.receive) {
          sub.context.receive(signal, signal.source);
        } else {
          sub.callback(signal, signal.source);
        }
        deliveryCount++;
      } catch (error) {
        console.error(`[MessageBus] Delivery error to ${sub.context.type}:${sub.context.id}:`, error);
      }
    });

    console.log(`[MessageBus] Signal '${type}' delivered to ${deliveryCount} subscribers`);
    return deliveryCount;
  }

  /**
   * Send a message directly to a specific target
   */
  static sendDirectly(signal, target) {
    if (!target || !target.receive) {
      console.error(`[MessageBus] Invalid target for direct sending`);
      return false;
    }

    // Log the message for audit and reflexivity
    this.logMessage({
      ...signal,
      directDelivery: true,
      target: {
        id: target.id,
        type: target.type
      }
    });

    try {
      target.receive(signal, signal.source);
      console.log(`[MessageBus] Signal '${signal.type}' delivered directly to ${target.type}:${target.id}`);
      return true;
    } catch (error) {
      console.error(`[MessageBus] Direct sending error to ${target.type}:${target.id}:`, error);
      return false;
    }
  }

  /**
   * Log a message for reflexive analysis
   */
  static logMessage(signal) {
    this.messageLog.push({
      timestamp: Date.now(),
      signal: { ...signal }
    });

    // Limit log size to 100 messages
    if (this.messageLog.length > 100) {
      this.messageLog.shift();
    }
  }

  /**
   * Retrieve recent messages for analysis
   */
  static getRecentMessages(count = 10, filterType = null) {
    let filtered = this.messageLog;

    if (filterType) {
      filtered = filtered.filter(entry => entry.signal.type === filterType);
    }

    return filtered.slice(-count);
  }
}

/**
 * HarmoniaInterpreter - Implements the processing of the HARMONIA language
 * This component is responsible for parsing and executing HARMONIA code
 */
class HarmoniaInterpreter extends CellularComponent {
  constructor() {
    super("core-interpreter", "HarmoniaInterpreter");

    // Initialize cellular sub-components
    this.parser = new CellularComponent("parser", "Parser");
    this.evaluator = new CellularComponent("evaluator", "Evaluator");
    this.transformer = new CellularComponent("transformer", "Transformer");

    // Configure the ATHENA interface
    this.athena = new AthenaInterface();

    // Execution context state
    this.context = {
      runtime: {},
      symbols: new Map(),
      cells: new Map(),
      reflectionData: [],
    };

    // Configure input/output membrane
    this.defineMembrane({
      permeable: ["code.execute", "code.evaluate", "code.transform"],
      semipermeable: ["meta.inspect", "reflection.request"],
      impermeable: ["system.shutdown"],
      filters: {
        "code.execute": (signal) => {
          // Clean and secure code before execution
          return {
            ...signal,
            data: {
              ...signal.data,
              code: this.sanitizeCode(signal.data.code)
            }
          };
        }
      }
    });

    // Configure signal receptors
    this.receptors = [
      {
        type: "code.execute",
        process: async (signal, source) => {
          try {
            const result = await this.executeCode(signal.data.code, signal.data.context);
            this.emit("code.result", { result, originalSignal: signal }, [source]);
          } catch (error) {
            this.emit("code.error", { error: error.message, originalSignal: signal }, [source]);
          }
        }
      },
      {
        type: "code.evaluate",
        process: async (signal, source) => {
          try {
            const evaluation = await this.evaluateCode(signal.data.code, signal.data.context);
            this.emit("evaluation.result", { evaluation, originalSignal: signal }, [source]);
          } catch (error) {
            this.emit("evaluation.error", { error: error.message, originalSignal: signal }, [source]);
          }
        }
      },
      {
        type: "reflection.request",
        process: async (signal, source) => {
          try {
            const reflection = await this.generateReflection(signal.data.target);
            this.emit("reflection.result", { reflection, originalSignal: signal }, [source]);
          } catch (error) {
            this.emit("reflection.error", { error: error.message, originalSignal: signal }, [source]);
          }
        }
      }
    ];

    // Subscribe to relevant notifications on the message bus
    MessageBus.subscribe("system.status", this.handleSystemStatus.bind(this), this);

    // Initialize periodic self-reflection
    this.initSelfReflection();

    this.log("HarmoniaInterpreter initialized successfully");
  }

  /**
   * Sanitize code to prevent malicious injections
   */
  sanitizeCode(code) {
    // Simplified version for POC
    // In a real implementation, apply full sandboxing
    return code
      .replace(/process\.exit/g, "/* forbidden */ null")
      .replace(/require\s*\(/g, "/* forbidden */ null(");
  }

  /**
   * Execute HARMONIA code
   */
  async executeCode(code, context = {}) {
    this.log(`Executing HARMONIA code (${code.length} characters)`);

    // Use parser to analyze code
    const parseResult = await this.parseCode(code);

    if (!parseResult.success) {
      throw new Error(`Parsing error: ${parseResult.error}`);
    }

    // Use evaluator to execute code
    const executeResult = await this.evaluateCode(parseResult.ast, {
      ...this.context,
      ...context
    });

    // Store execution data for self-reflection
    this.context.reflectionData.push({
      timestamp: Date.now(),
      code,
      parseResult,
      executeResult,
      context
    });

    return executeResult;
  }

  /**
   * Parse HARMONIA code into AST (Abstract Syntax Tree)
   */
  async parseCode(code) {
    // For POC, simulate simplified parsing
    // In a real implementation, this would be a full parser
    this.log("Parsing code");

    if (!code || code.trim().length === 0) {
      return {
        success: false,
        error: "Empty code"
      };
    }

    try {
      // Simulate a simple syntax tree for POC
      const ast = {
        type: "Program",
        body: code.split('\n').map((line, index) => {
          return {
            type: "Statement",
            content: line,
            lineNumber: index + 1
          };
        }),
        metadata: {
          length: code.length,
          lines: code.split('\n').length
        }
      };

      return {
        success: true,
        ast
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Evaluate parsed HARMONIA code
   */
  async evaluateCode(ast, context = {}) {
    this.log("Evaluating HARMONIA code");

    // For POC, simulate execution
    // In a real implementation, this would be a full evaluator

    try {
      // Simulate execution result
      return {
        success: true,
        result: `Successfully executed ${ast.metadata.lines} lines of HARMONIA code`,
        context: context,
        metrics: {
          executionTime: Math.random() * 100, // ms
          memoryUsage: Math.random() * 1024, // kb
          cellsCreated: Math.floor(Math.random() * 5)
        }
      };
    } catch (error) {
      throw new Error(`Evaluation error: ${error.message}`);
    }
  }

  /**
   * System notification handler
   */
  handleSystemStatus(signal) {
    this.log(`System notification received: ${signal.data.status}`);

    // Update internal state based on system status
    if (signal.data.status === "low_resources") {
      this.metabolism.energyConsumption *= 0.7; // Reduce consumption
      this.log("Metabolic adaptation: reduced energy consumption", "info");
    }
  }

  /**
   * Initialize periodic self-reflection
   */
  initSelfReflection() {
    setInterval(async () => {
      // Check metabolic state before starting reflection
      const currentEnergy = this.processMetabolism();

      if (currentEnergy < 0.3) {
        this.log("Insufficient energy for self-reflection, postponed", "warn");
        return;
      }

      await this.performSelfReflection();

    }, SYSTEM_CONFIG.selfReflectionInterval);

    this.log("Periodic self-reflection initialized");
  }

  /**
   * Perform self-reflection using ATHENA
   */
  async performSelfReflection() {
    this.log("Starting self-reflection process");
    this.state.lastReflection = Date.now();

    // For POC, extract current code (simulated)
    const currentCode = this.extractSelfCode();

    // Analyze and evaluate with ATHENA
    try {
      const evaluation = await this.athena.evaluateCode(currentCode, {
        stage: "development",
        purpose: "self-reflection",
        metrics: {
          uptime: Date.now() - (this.state.startTime || Date.now()),
          energyLevel: this.state.energy,
          messageProcessed: MessageBus.messageLog.length
        }
      });

      this.log(`Reflexive evaluation completed: overall score ${evaluation.metrics.overallHealth.toFixed(2)}`);

      // If improvements are suggested and score is below 0.8
      if (evaluation.transformations.length > 0 && evaluation.metrics.overallHealth < 0.8) {
        this.log(`${evaluation.transformations.length} transformations suggested, applying...`);

        // Apply suggested transformations
        const transformation = await this.athena.transformCode(
          currentCode,
          evaluation.transformations,
          { source: "self-reflection" }
        );

        if (transformation.success) {
          this.log("Self-transformation successful!", "info");

          // In a real implementation, apply changes to the system itself
          // (hot-reloading or scheduled update)

          // Simulate transformation result
          this.emit("reflection.transformation", {
            before: evaluation.metrics,
            after: transformation.verification.metrics,
            changes: evaluation.transformations.length
          });
        }
      } else {
        this.log("No transformations needed at this time");
      }

      return evaluation;
    } catch (error) {
      this.log(`Error during self-reflection: ${error.message}`, "error");
      return null;
    }
  }

  /**
   * Extract current system code for self-analysis
   * In a real implementation, would access actual source code
   */
  extractSelfCode() {
    // Simulate code extraction for POC
    return `
// Example HARMONIA code for self-reflection test
cell FinancialAnalyzer {
  receptors {
    MarketData : gradient<PriceTimeSeries>;
    RiskTolerance : signal<float, 0.0..1.0>;
  }

  membrane {
    permeable_to(MarketData) when (signal_strength > threshold);

    // Outgoing communication
    emit AllocationRecommendation to global_gradient;
  }

  metabolism {
    for (let i = 0; i < resources.length; i++) {
      // Resource processing with traditional loop
      console.log("Processing resource:", resources[i]);
    }

    // Asynchronous operation without error handling
    await fetchExternalData();
  }
}
    `;
  }

  /**
   * Generate reflection on a specific target
   */
  async generateReflection(target) {
    this.log(`Generating reflection for target: ${target}`);

    // Collect relevant data for the target
    let reflectionData = {};

    if (target === "system") {
      reflectionData = {
        components: [...this.context.cells.keys()],
        messageCount: MessageBus.messageLog.length,
        uptime: Date.now() - (this.state.startTime || Date.now()),
        health: this.state.health,
        energy: this.state.energy
      };
    } else if (target === "communication") {
      // Analyze recent communications
      const recentMessages = MessageBus.getRecentMessages(20);
      const messageTypes = new Set(recentMessages.map(m => m.signal.type));

      reflectionData = {
        messageTypes: [...messageTypes],
        messageVolume: recentMessages.length,
        topSenders: this.analyzeTopSenders(recentMessages),
        patterns: this.detectCommunicationPatterns(recentMessages)
      };
    }

    // Use ATHENA to analyze this data
    try {
      // For POC, generate a simulated reflection
      return {
        success: true,
        timestamp: Date.now(),
        target,
        insights: [
          {
            type: "observation",
            content: `The system shows an energy balance that is ${reflectionData.energy > 0.7 ? 'optimal' : 'sub-optimal'}.`
          },
          {
            type: "pattern",
            content: "Communications follow a gradient diffusion model, suggesting an effective biomimetic approach."
          },
          {
            type: "recommendation",
            content: "Increase membrane permeability for low-priority signals to optimize processing."
          }
        ],
        metrics: {
          clarity: Math.random() * 0.3 + 0.7,
          relevance: Math.random() * 0.2 + 0.8,
          actionability: Math.random() * 0.4 + 0.6
        }
      };
    } catch (error) {
      this.log(`Error generating reflection: ${error.message}`, "error");
      throw error;
    }
  }

  /**
   * Analyze most frequent senders in recent messages
   */
  analyzeTopSenders(messages) {
    const senderCount = {};

    messages.forEach(msg => {
      const senderId = msg.signal.source ? `${msg.signal.source.type}:${msg.signal.source.id}` : 'unknown';
      senderCount[senderId] = (senderCount[senderId] || 0) + 1;
    });

    return Object.entries(senderCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([sender, count]) => ({ sender, count }));
  }

  /**
   * Detect communication patterns in recent messages
   */
  detectCommunicationPatterns(messages) {
    // Simplified version for POC
    // A real implementation would use pattern detection algorithms

    const patterns = [];

    // Detect repetitive sequences of message types
    const typeSequence = messages.map(m => m.signal.type).join(',');

    if (typeSequence.includes('code.execute,code.result,code.execute,code.result')) {
      patterns.push({
        name: "Repetitive execution loop",
        significance: "Could indicate an iterative process or excessive redundancy"
      });
    }

    if (messages.filter(m => m.signal.type === 'reflection.request').length > 3) {
      patterns.push({
        name: "Intensive reflection",
        significance: "The system is actively seeking improvement and adaptation"
      });
    }

    return patterns;
  }
}

/**
 * HumanInterface - Interface between humans and HARMONIA
 * Facilitates bidirectional communication between programmers and the system
 */
class HumanInterface extends CellularComponent {
  constructor() {
    super("human-interface", "HumanInterface");

    // Configure interface
    this.inputBuffer = [];
    this.outputBuffer = [];
    this.interpreter = null; // Reference to HARMONIA interpreter

    // Configure membrane for accepted signal types
    this.defineMembrane({
      permeable: [
        "human.input",
        "human.command",
        "code.result",
        "evaluation.result",
        "reflection.result"
      ],
      impermeable: ["system.internal"],
      filters: {}
    });

    // Configure receptors
    this.receptors = [
      {
        type: "human.input",
        process: (signal) => {
          this.handleHumanInput(signal.data.input, signal.data.context);
        }
      },
      {
        type: "code.result",
        process: (signal) => {
          this.displayResult(signal.data.result);
        }
      },
      {
        type: "evaluation.result",
        process: (signal) => {
          this.displayEvaluation(signal.data.evaluation);
        }
      },
      {
        type: "reflection.result",
        process: (signal) => {
          this.displayReflection(signal.data.reflection);
        }
      }
    ];

    this.log("Human interface initialized");
  }

  /**
   * Connect the interface to the HARMONIA interpreter
   */
  connectToInterpreter(interpreter) {
    this.interpreter = interpreter;
    this.log(`Connected to interpreter ${interpreter.id}`);
  }

  /**
   * Process human input and send it to the system
   */
  handleHumanInput(input, context = {}) {
    this.log(`Human input received: ${input.substring(0, 50)}...`);

    // Parse command
    if (input.startsWith('/')) {
      this.handleCommand(input.substring(1), context);
      return;
    }

    // Treat input as HARMONIA code
    if (this.interpreter) {
      this.emit("code.execute", {
        code: input,
        context: {
          source: "human",
          ...context
        }
      }, [this.interpreter]);

      this.log("Code sent to interpreter");
    } else {
      this.displayOutput("Error: Interpreter not connected");
    }
  }

  /**
   * Process special commands
   */
  handleCommand(command, context = {}) {
    const [cmd, ...args] = command.split(' ');

    switch (cmd.toLowerCase()) {
      case 'eval':
      case 'evaluate':
        // Request code evaluation without execution
        if (args.length > 0 && this.interpreter) {
          const code = args.join(' ');
          this.emit("code.evaluate", {
            code,
            context: {
              source: "human",
              ...context
            }
          }, [this.interpreter]);

          this.log("Evaluation request sent");
        } else {
          this.displayOutput("Usage: /eval <code>");
        }
        break;

      case 'reflect':
        // Request reflection on a system aspect
        if (args.length > 0 && this.interpreter) {
          const target = args[0];
          this.emit("reflection.request", {
            target,
            context: {
              source: "human",
              ...context
            }
          }, [this.interpreter]);

          this.log(`Reflection request for '${target}' sent`);
        } else {
          this.displayOutput("Usage: /reflect <system|communication|code>");
        }
        break;

      case 'help':
        this.displayHelp();
        break;

      default:
        this.displayOutput(`Unknown command: ${cmd}\nUse /help to see available commands.`);
    }
  }

  /**
   * Display command help
   */
  displayHelp() {
    this.displayOutput(`
HARMONIA POC - Available Commands:

/eval <code>   - Evaluate HARMONIA code without executing it
/reflect <target> - Generate reflection on a system aspect
                 Valid targets: system, communication, code
/help         - Display this help

By default, any text not starting with / is treated as
HARMONIA code to execute.
    `);
  }

  /**
   * Display execution result
   */
  displayResult(result) {
    this.displayOutput(`
=== Execution Result ===
${result.result}

Metrics:
- Execution Time: ${result.metrics.executionTime.toFixed(2)} ms
- Memory Usage: ${result.metrics.memoryUsage.toFixed(2)} kb
- Cells Created: ${result.metrics.cellsCreated}
    `);
  }

  /**
   * Display evaluation result
   */
  displayEvaluation(evaluation) {
    const issuesText = evaluation.issues.map(issue =>
      `[${issue.severity.toUpperCase()}] ${issue.description}\n  → ${issue.recommendation}`
    ).join('\n');

    this.displayOutput(`
=== Code Evaluation ===
Overall Health: ${evaluation.metrics.overallHealth.toFixed(2)}
Structural Biomimicry: ${evaluation.metrics.structuralBiomimicry.toFixed(2)}
Performance: ${evaluation.metrics.performance.toFixed(2)}
Adaptability: ${evaluation.metrics.adaptability.toFixed(2)}

${evaluation.issues.length > 0 ? `Issues Detected (${evaluation.issues.length}):\n${issuesText}` : 'No issues detected.'}

Recommendations:
${evaluation.recommendations.map(r => `- ${r.description}`).join('\n')}
    `);
  }

  /**
   * Display reflection result
   */
  displayReflection(reflection) {
    this.displayOutput(`
=== Reflection on ${reflection.target} ===

Observations:
${reflection.insights.map(i => `- ${i.content}`).join('\n')}

Clarity: ${reflection.metrics.clarity.toFixed(2)}
Relevance: ${reflection.metrics.relevance.toFixed(2)}
Actionability: ${reflection.metrics.actionability.toFixed(2)}
    `);
  }

  /**
   * Display a message in the interface
   */
  displayOutput(message) {
    console.log("\n" + message + "\n");
    this.outputBuffer.push({
      timestamp: Date.now(),
      message
    });

    // Keep only the last 50 messages
    if (this.outputBuffer.length > 50) {
      this.outputBuffer.shift();
    }
  }
}

/**
 * Main function to initialize the HARMONIA POC system
 */
function initHarmoniaMVP() {
  console.log(`
=====================================================
  HARMONIA POC - Reflexive System with ATHENA
  Version: ${SYSTEM_CONFIG.version}
=====================================================
  `);

  // Create main components
  const interpreter = new HarmoniaInterpreter();
  const humanInterface = new HumanInterface();

  // Connect components
  humanInterface.connectToInterpreter(interpreter);

  // Set start date
  interpreter.state.startTime = Date.now();

  // Simulate user inputs for demonstration
  setTimeout(() => {
    console.log("\n=== Automatic Demonstration ===\n");

    // Simulate a code evaluation request
    humanInterface.handleHumanInput("/eval cell TestCell { receptors { Data: signal<json>; } membrane { permeable_to(Data); emit Response to neighbors; } }", {
      demo: true
    });

    // After a few seconds, simulate a reflection request
    setTimeout(() => {
      humanInterface.handleHumanInput("/reflect system", { demo: true });
    }, 3000);

    // After a few more seconds, simulate code execution
    setTimeout(() => {
      humanInterface.handleHumanInput(`
cell AnalyticsProcessor {
  receptors {
    InputData: gradient<DataFrame>;
    ConfigParams: signal<json>;
  }

  membrane {
    permeable_to(InputData) when (validation_score > 0.8);
    permeable_to(ConfigParams);

    emit ProcessedData to global_gradient;
    emit StatusUpdate to local_neighbors;
  }

  metabolism {
    energy_consumption = adaptive(workload);
    priority = contextual(system_needs);

    for (let i = 0; i < data_chunks.length; i++) {
      console.log("Processing chunk:", i);
      // Data processing
    }

    await fetchExternalResources();
  }
}
      `, { demo: true });
    }, 6000);

  }, 1000);

  return {
    interpreter,
    humanInterface
  };
}

// Initialize the system if executed directly
if (typeof require !== 'undefined' && require.main === module) {
  const system = initHarmoniaMVP();
}

// Export components for use in other modules
module.exports = {
  CellularComponent,
  AthenaInterface,
  MessageBus,
  HarmoniaInterpreter,
  HumanInterface,
  initHarmoniaMVP
};