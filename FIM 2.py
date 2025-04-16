import random
from flask import Flask, render_template_string, request, jsonify
import webbrowser

# Flask app setup
app = Flask(__name__)

# List of numbers for the test
my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Settings (Global)
selected_type = 'Addition'  # Default test type
problems = []

def generate_operation(operation):
    """Return the operation function based on the operation type."""
    operations = {
        'Addition': lambda x, y: (x + y),
        'Subtraction': lambda x, y: (x - y) if x >= y else (y - x),
        'Multiplication': lambda x, y: (x * y),
        'Division': lambda x, y: (x // y) if y != 0 and x % y == 0 else None
    }
    return operations.get(operation, lambda x, y: None)

def assign_random_values(my_list, num_iterations, operation_func):
    """Generate unique pairs with results."""
    all_pairs = set()

    while len(all_pairs) < num_iterations:
        var1, var2 = random.sample(my_list, 2)
        result = operation_func(var1, var2)
        if result is not None:
            all_pairs.add((var1, var2, result))

    return list(all_pairs)

def generate_problems():
    """Generate 100 random problems from the 10x10 grid."""
    problems = []
    operation_func = generate_operation(selected_type)
    
    # Create all possible combinations
    all_combinations = []
    for i in range(1, 11):
        for j in range(1, 11):
            result = operation_func(i, j)
            if result is not None:
                all_combinations.append((i, j, result))
    
    # Randomly select 100 problems (with replacement)
    for _ in range(100):
        problems.append(random.choice(all_combinations))
    
    print(f"Sample problem: {problems[0]}")  # Debug log
    return problems

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>10x10 Mathematics Test</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        :root {
          --main-bg: #f5f5f5;
          --accent: #4CAF50;
          --accent-hover: #45a049;
          --text: #333;
          --grid-border: #ddd;
          --input-bg: #fff;
          --input-text: #333;
          --button-radius: 8px;
          --transition: 0.2s;
        }
        body {
          margin: 0;
          font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
          background: var(--main-bg);
          color: var(--text);
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        header {
          background: #fff;
          padding: 1rem 2rem;
          font-size: 1.5rem;
          font-weight: bold;
          letter-spacing: 1px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .container {
          display: flex;
          flex: 1;
          padding: 1rem;
          gap: 1rem;
          justify-content: center;
          align-items: flex-start;
          max-width: 1400px;
          margin: 0 auto;
        }
        .sidebar {
          min-width: 250px;
          max-width: 300px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          background: #fff;
          padding: 1.5rem;
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .grid-area {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
          max-width: 700px;
        }
        .math-grid {
          display: grid;
          grid-template-columns: repeat(10, 60px);
          grid-template-rows: repeat(10, 60px);
          gap: 3px;
          background: var(--grid-border);
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          padding: 10px;
          margin-bottom: 1rem;
        }
        .math-grid div {
          background: #fff;
          border-radius: 4px;
          border: 1px solid #ddd;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1rem;
          color: #222;
          transition: all 0.2s ease;
          font-weight: bold;
          text-align: center;
          padding: 5px;
          word-break: break-word;
        }
        .math-grid div.correct {
          color: #2e7d32;
          background-color: #e8f5e9;
          border-color: #2e7d32;
        }
        .math-grid div.incorrect {
          color: #c62828;
          background-color: #ffebee;
          border-color: #c62828;
        }
        .test-type {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }
        .test-type label {
          font-size: 1rem;
          font-weight: 500;
        }
        .test-type select {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: var(--button-radius);
          font-size: 1rem;
        }
        .problem-display {
          background: var(--input-bg);
          color: var(--input-text);
          border: 1px solid #ddd;
          border-radius: var(--button-radius);
          padding: 1rem;
          font-size: 1.5rem;
          text-align: center;
          font-weight: bold;
        }
        .numpad {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        .numpad button {
          background: var(--accent);
          color: white;
          border: none;
          border-radius: var(--button-radius);
          padding: 1rem;
          font-size: 1.2rem;
          font-weight: bold;
          cursor: pointer;
          transition: background var(--transition);
        }
        .numpad button:hover {
          background: var(--accent-hover);
        }
        .numpad .enter, .numpad .backspace {
          grid-column: span 1;
        }
        .score-display {
          background: #666;
          color: white;
          padding: 0.5rem 1rem;
          border-radius: var(--button-radius);
          font-weight: bold;
          text-align: center;
        }
        .start-test {
          background: var(--accent);
          color: white;
          border: none;
          border-radius: var(--button-radius);
          padding: 1rem;
          font-size: 1.1rem;
          font-weight: bold;
          cursor: pointer;
          transition: background var(--transition);
        }
        .start-test:hover {
          background: var(--accent-hover);
        }
        footer {
          background: #fff;
          color: #666;
          text-align: center;
          padding: 1rem 0;
          font-size: 0.9rem;
          box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
        }
        .timer {
          position: fixed;
          bottom: 100px;
          right: 20px;
          background: var(--accent);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: var(--button-radius);
          font-weight: bold;
          font-size: 1.2rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .progress-table {
          position: relative;
          display: flex;
          flex-direction: row;
          gap: 2px;
          background: #fff;
          padding: 10px;
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: auto;
          height: 25px;
          margin: 0 auto;
          width: 800px;
          justify-content: center;
        }
        .progress-line {
          width: 6px;
          height: 100%;
          background: #ddd;
          border-radius: 3px;
          transition: all 0.3s ease;
        }
        .progress-line.completed {
          background: var(--accent);
        }
        .progress-line.partition {
          width: 3px;
          background: #999;
          margin: 0 4px;
        }
        .problem-counter {
          text-align: center;
          font-size: 1.2rem;
          font-weight: bold;
          color: #333;
          background: #fff;
          padding: 10px;
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 800px;
          margin: 0 auto;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        @media (max-width: 900px) {
          .container {
            flex-direction: column;
            align-items: center;
            padding: 1rem;
          }
          .sidebar {
            width: 100%;
            max-width: 500px;
          }
          .math-grid {
            grid-template-columns: repeat(10, 60px);
            grid-template-rows: repeat(10, 60px);
          }
          .math-grid div {
            width: 60px;
            height: 60px;
            font-size: 1rem;
          }
        }
        @media (max-width: 600px) {
          .math-grid {
            grid-template-columns: repeat(10, 50px);
            grid-template-rows: repeat(10, 50px);
          }
          .math-grid div {
            width: 50px;
            height: 50px;
            font-size: 0.9rem;
          }
        }
      </style>
    </head>
    <body>
      <header>
        10x10 Mathematics Test
      </header>
      <div class="container">
        <aside class="sidebar">
          <div class="test-type">
            <label for="testType">Test Type:</label>
            <select id="testType">
              <option value="Addition">Addition</option>
              <option value="Subtraction">Subtraction</option>
              <option value="Multiplication">Multiplication</option>
              <option value="Division">Division</option>
            </select>
          </div>
          <div class="problem-display" id="display">Select test type and click Start Test</div>
          <div class="numpad">
            <button onclick="handleNumberInput(1)">1</button>
            <button onclick="handleNumberInput(2)">2</button>
            <button onclick="handleNumberInput(3)">3</button>
            <button onclick="handleNumberInput(4)">4</button>
            <button onclick="handleNumberInput(5)">5</button>
            <button onclick="handleNumberInput(6)">6</button>
            <button onclick="handleNumberInput(7)">7</button>
            <button onclick="handleNumberInput(8)">8</button>
            <button onclick="handleNumberInput(9)">9</button>
            <button onclick="handleNumberInput(0)">0</button>
            <button class="backspace" onclick="handleBackspace()">⌫</button>
            <button class="enter" onclick="checkAnswer()">Enter</button>
          </div>
          <button class="start-test" onclick="startTest()">Start Test</button>
        </aside>
        <main class="grid-area">
          <div class="math-grid" id="grid">
            <!-- Grid cells will be populated by JavaScript -->
          </div>
          <div class="progress-table" id="progress-table">
            <!-- Progress lines will be populated by JavaScript -->
          </div>
          <div class="problem-counter" id="problem">Problem: 1/100</div>
        </main>
      </div>
      <div class="timer" id="timer">5:00</div>
      <footer>
        &copy; 2025 Mathematics Test App. All rights reserved.
      </footer>
      <script>
        let currentAnswer = '';
        let problems = [];
        let currentProblemIndex = 0;
        let correctAnswers = 0;
        let totalAnswers = 0;
        let selectedType = 'Addition';
        let timeLeft = 300;
        let timerInterval;
        let usedProblems = new Set();

        function updateTimer() {
          const minutes = Math.floor(timeLeft / 60);
          const seconds = timeLeft % 60;
          document.getElementById('timer').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
          
          if (timeLeft <= 0) {
            clearInterval(timerInterval);
            endTest();
          }
          timeLeft--;
        }

        function initializeGrid() {
          const grid = document.getElementById('grid');
          grid.innerHTML = '';
          for (let i = 0; i < 10; i++) {
            for (let j = 0; j < 10; j++) {
              const cell = document.createElement('div');
              cell.dataset.row = i;
              cell.dataset.col = j;
              cell.textContent = '';  // Initialize with empty content
              grid.appendChild(cell);
            }
          }
        }

        function updateProgress() {
          const progressTable = document.getElementById('progress-table');
          if (!progressTable) return;  // Safety check
          
          progressTable.innerHTML = '';
          
          for (let i = 0; i < 100; i++) {
            const line = document.createElement('div');
            line.className = 'progress-line';
            if (i < currentProblemIndex) {
              line.classList.add('completed');
            }
            if (i % 25 === 24) {  // Add partition every 25 problems
              const partition = document.createElement('div');
              partition.className = 'progress-line partition';
              progressTable.appendChild(partition);
            }
            progressTable.appendChild(line);
          }
        }

        function startTest() {
          selectedType = document.getElementById('testType').value;
          currentAnswer = '';
          currentProblemIndex = 0;
          correctAnswers = 0;
          totalAnswers = 0;
          timeLeft = 300;
          usedProblems.clear();
          
          // Remove focus from all elements
          document.activeElement.blur();
          
          // Clear any existing timer
          if (timerInterval) {
            clearInterval(timerInterval);
          }
          
          // Initialize timer
          timerInterval = setInterval(updateTimer, 1000);
          
          // Initialize grid and progress
          initializeGrid();
          updateProgress();
          
          // Fetch problems from server
          fetch(`/get_problems?type=${encodeURIComponent(selectedType)}`)
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              return response.json();
            })
            .then(data => {
              console.log('Received problems:', data);
              problems = data;
              if (problems.length > 0) {
                const [num1, num2, _] = problems[0];
                document.getElementById('display').textContent = 
                  `${num1} ${getOperationSign()} ${num2} = _`;
                document.getElementById('problem').textContent = 'Problem: 1/100';
                document.getElementById('timer').textContent = '5:00';
              } else {
                document.getElementById('display').textContent = 'No problems available. Please try again.';
              }
            })
            .catch(error => {
              console.error('Error fetching problems:', error);
              document.getElementById('display').textContent = 'Error starting test. Please try again.';
            });
        }

        function getOperationSign() {
          switch(selectedType) {
            case 'Addition': return '+';
            case 'Subtraction': return '-';
            case 'Multiplication': return '×';
            case 'Division': return '÷';
            default: return '+';
          }
        }

        function handleNumberInput(number) {
          if (currentProblemIndex < problems.length) {
            currentAnswer += number.toString();
            const [num1, num2] = problems[currentProblemIndex];
            document.getElementById('display').textContent = 
              `${num1} ${getOperationSign()} ${num2} = ${currentAnswer}`;
          }
        }

        function handleBackspace() {
          if (currentAnswer.length > 0) {
            currentAnswer = currentAnswer.slice(0, -1);
            const [num1, num2] = problems[currentProblemIndex];
            document.getElementById('display').textContent = 
              `${num1} ${getOperationSign()} ${num2} = ${currentAnswer || '_'}`;
          }
        }

        function checkAnswer() {
          if (currentAnswer && currentProblemIndex < problems.length) {
            const [num1, num2, correctResult] = problems[currentProblemIndex];
            const userAnswer = parseInt(currentAnswer);
            
            totalAnswers++;
            
            // For division, we need to find the cell based on the divisor and result
            let row, col;
            if (selectedType === 'Division') {
              row = num2 - 1;  // Use divisor for row
              col = correctResult - 1;  // Use result for column
            } else {
              row = num1 - 1;
              col = num2 - 1;
            }
            
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            
            if (userAnswer === correctResult) {
              correctAnswers++;
              cell.textContent = `${num1}${getOperationSign()}${num2}`;
              cell.classList.add('correct');
              cell.classList.remove('incorrect');
            } else {
              cell.textContent = `${num1}${getOperationSign()}${num2}`;
              cell.classList.add('incorrect');
              cell.classList.remove('correct');
            }

            currentProblemIndex++;
            updateProgress();
            
            if (currentProblemIndex < problems.length) {
              currentAnswer = '';
              const [nextNum1, nextNum2, _] = problems[currentProblemIndex];
              document.getElementById('display').textContent = 
                `${nextNum1} ${getOperationSign()} ${nextNum2} = _`;
              document.getElementById('problem').textContent = 
                `Problem: ${currentProblemIndex + 1}/100`;
            } else {
              clearInterval(timerInterval);
              document.getElementById('display').textContent = 
                `Game Over! Final Score: ${correctAnswers}/${totalAnswers}`;
              const accuracy = (correctAnswers / totalAnswers) * 100;
              document.getElementById('problem').textContent = 
                `Final Score: ${correctAnswers}/${totalAnswers} (${accuracy.toFixed(1)}%)`;
            }
          }
        }

        function endTest() {
          clearInterval(timerInterval);
          document.getElementById('display').textContent = 
            `Time's up! Final Score: ${correctAnswers}/${totalAnswers}`;
          const accuracy = (correctAnswers / totalAnswers) * 100;
          document.getElementById('problem').textContent = 
            `Final Score: ${correctAnswers}/${totalAnswers} (${accuracy.toFixed(1)}%)`;
        }

        // Initialize grid and progress on page load
        document.addEventListener('DOMContentLoaded', () => {
          initializeGrid();
          updateProgress();
          
          // Add event listener for test type change
          document.getElementById('testType').addEventListener('change', () => {
            document.getElementById('display').textContent = 'Select test type and click Start Test';
            currentAnswer = '';
            currentProblemIndex = 0;
            correctAnswers = 0;
            totalAnswers = 0;
            timeLeft = 300;
            usedProblems.clear();
            if (timerInterval) {
              clearInterval(timerInterval);
            }
            document.getElementById('timer').textContent = '5:00';
            document.getElementById('problem').textContent = 'Problem: 1/100';
            initializeGrid();
            updateProgress();
          });
        });

        // Keyboard support
        document.addEventListener('keydown', (event) => {
          // Prevent default tab behavior
          if (event.key === 'Tab') {
            event.preventDefault();
            return;
          }
          
          if (event.key >= '0' && event.key <= '9') {
            handleNumberInput(parseInt(event.key));
          } else if (event.key === 'Backspace') {
            handleBackspace();
          } else if (event.key === 'Enter') {
            checkAnswer();
          }
        });

        // Prevent tabbing to elements
        document.addEventListener('focus', (event) => {
          if (currentProblemIndex > 0) {  // If test has started
            event.target.blur();
          }
        }, true);
      </script>
    </body>
    </html>
    ''')

@app.route('/get_problems')
def get_problems():
    global problems, selected_type
    selected_type = request.args.get('type', 'Addition')
    print(f"Generating problems for test type: {selected_type}")
    
    # Generate 100 unique problems
    problems = []
    operation_func = generate_operation(selected_type)
    
    # Create all possible combinations
    all_combinations = []
    if selected_type == 'Subtraction':
        # For subtraction, generate problems up to 20
        for i in range(1, 21):  # First number can be up to 20
            for j in range(1, 11):  # Second number up to 10
                if i > j:  # Only include if first number is larger
                    result = i - j
                    if 0 <= result <= 10:  # Only include if result is between 0 and 10
                        all_combinations.append((i, j, result))
    elif selected_type == 'Division':
        # For division, generate problems with larger number from 100 to 1
        for i in range(100, 0, -1):  # First number from 100 to 1
            for j in range(1, 11):  # Second number from 1 to 10
                if i % j == 0:  # Only include if division is exact
                    result = i // j
                    if 1 <= result <= 10:  # Only include if result is between 1 and 10
                        all_combinations.append((i, j, result))
    else:
        # For other operations, use the original logic
        for i in range(1, 11):
            for j in range(1, 11):
                result = operation_func(i, j)
                if result is not None:
                    all_combinations.append((i, j, result))
    
    # Randomly select 100 problems without replacement
    if len(all_combinations) >= 100:
        problems = random.sample(all_combinations, 100)
    else:
        # If not enough unique combinations, fill with random selections
        problems = all_combinations.copy()
        while len(problems) < 100:
            problems.append(random.choice(all_combinations))
    
    # Shuffle the problems to ensure random order
    random.shuffle(problems)
    
    print(f"Generated {len(problems)} problems")
    print(f"Sample problems: {problems[:5]}")  # Debug log
    return jsonify(problems)

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # Start Flask
    webbrowser.open('http://localhost:5000')
    app.run(port=5000)
