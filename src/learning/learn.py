import argparse
import os
import importlib
from datetime import datetime
from typing import Type, Dict, Any
from ..scenarios.base import Scenario
from ..intelligences.base import Intelligence
from .learning_mode import LearningMode
from ..registry import SCENARIOS, INTELLIGENCES, get_choices
from ..utils.load_class import load_class

def load_class(class_path: str) -> Type[Any]:
    """Dynamically load a class from a string path."""
    module_path, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def list_available_options():
    """Print available scenarios and intelligences."""
    print("\nAvailable Scenarios:")
    for name in SCENARIOS:
        print(f"  - {name}")
    
    print("\nAvailable Intelligences:")
    for name in INTELLIGENCES:
        print(f"  - {name}")

def main():
    parser = argparse.ArgumentParser(description='Run learning mode for bot evolution')
    
    # Mode selection
    parser.add_argument('--mode', choices=['learn', 'demo'], default='learn',
                      help='Mode to run in: learn (evolve new weights) or demo (show best weights)')
    
    # Scenario and Intelligence selection
    parser.add_argument('--scenario', type=str, default='free_roam',
                      choices=get_choices(SCENARIOS),
                      help=f'Scenario to use (default: free_roam)')
    parser.add_argument('--intelligence', type=str, default='flocking',
                      choices=get_choices(INTELLIGENCES),
                      help=f'Intelligence type to use (default: flocking)')
    parser.add_argument('--list', action='store_true',
                      help='List available scenarios and intelligences')
    
    # Learning parameters
    parser.add_argument('--generations', type=int, default=100,
                      help='Number of generations to evolve (default: 100)')
    parser.add_argument('--population-size', type=int, default=50,
                      help='Number of individuals in population (default: 50)')
    parser.add_argument('--generation-frames', type=int, default=500,
                      help='Number of frames to simulate per generation (default: 500)')
    
    # Evolution parameters
    parser.add_argument('--mutation-rate', type=float, default=0.1,
                      help='Probability of mutating each weight (default: 0.1)')
    parser.add_argument('--mutation-range', type=float, default=0.2,
                      help='Range of mutation effect (default: 0.2)')
    parser.add_argument('--elite-percentage', type=float, default=0.1,
                      help='Percentage of top performers to keep unchanged (default: 0.1)')
    parser.add_argument('--tournament-size', type=int, default=5,
                      help='Number of individuals in each tournament selection (default: 5)')
    
    # Save/load parameters
    parser.add_argument('--save-dir', type=str, default=None,
                      help='Directory to save evolution progress (default: auto-generated)')
    parser.add_argument('--load-weights', type=str, default=None,
                      help='Load initial weights from file (default: None)')
    
    # Visualization parameters
    parser.add_argument('--visualize', action='store_true',
                      help='Show real-time visualization of evolution progress')
    
    # Demo parameters
    parser.add_argument('--num-bots', type=int, default=30,
                      help='Number of bots to use in demo mode (default: 30)')
    
    args = parser.parse_args()
    
    # Just list available options and exit if requested
    if args.list:
        list_available_options()
        return
    
    # Load scenario and intelligence classes
    scenario_class = load_class(SCENARIOS[args.scenario])
    intelligence_class = load_class(INTELLIGENCES[args.intelligence])
    
    # Create save directory with descriptive name if not specified
    if args.save_dir is None and args.mode == 'learn':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.save_dir = os.path.join(
            'evolution_results',
            f'{args.scenario}_{args.intelligence}_{timestamp}'
        )
    
    # Initialize learning mode
    learning = LearningMode(
        scenario_class=scenario_class,
        intelligence_class=intelligence_class,
        population_size=args.population_size,
        generation_frames=args.generation_frames,
        mutation_rate=args.mutation_rate,
        mutation_range=args.mutation_range,
        elite_percentage=args.elite_percentage,
        tournament_size=args.tournament_size,
        visualize=args.visualize
    )
    
    if args.mode == 'learn':
        # Load initial weights if specified
        if args.load_weights:
            print(f"\nLoading initial weights from: {args.load_weights}")
            learning.load_weights(args.load_weights)
        
        # Print configuration
        print("\nStarting evolution with:")
        print(f"Scenario: {args.scenario}")
        print(f"Intelligence: {args.intelligence}")
        print(f"\nEvolution parameters:")
        print(f"- Generations: {args.generations}")
        print(f"- Population size: {args.population_size}")
        print(f"- Tournament size: {args.tournament_size}")
        print(f"- Elite percentage: {args.elite_percentage*100}%")
        print(f"- Mutation rate: {args.mutation_rate}")
        print(f"- Mutation range: ±{args.mutation_range*100}%")
        print(f"\nSaving results to: {args.save_dir}")
        
        # Run evolution
        stats_history = learning.run_evolution(args.generations, args.save_dir)
        
        # Print final results
        best_gen = max(stats_history, key=lambda x: x.max_fitness)
        print("\nEvolution complete!")
        print(f"Best fitness: {best_gen.max_fitness:.3f} (Generation {best_gen.generation})")
        print(f"Best weights: {best_gen.best_weights}")
        print(f"Results saved in: {args.save_dir}")
        
        # Offer to run demo with best weights
        best_weights_file = os.path.join(args.save_dir, f"gen_{best_gen.generation:04d}_best_weights.json")
        print("\nTo see these results in action, run:")
        print(f"python learn.py --mode demo --load-weights {best_weights_file}")
    
    else:  # Demo mode
        if not args.load_weights:
            print("Error: Must specify --load-weights in demo mode")
            return
        
        print(f"\nRunning demo with:")
        print(f"- Scenario: {args.scenario}")
        print(f"- Intelligence: {args.intelligence}")
        print(f"- Number of bots: {args.num_bots}")
        print(f"- Weights file: {args.load_weights}")
        
        learning.demo_best_weights(args.load_weights, args.num_bots)

if __name__ == "__main__":
    main() 