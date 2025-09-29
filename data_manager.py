"""
Data Manager - Handles data storage, retrieval, and context management.
"""
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """Manages data storage and retrieval for the agent system."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the data manager."""
        self.data_dir = data_dir
        self.interactions_file = os.path.join(data_dir, "interactions.jsonl")
        self.context_file = os.path.join(data_dir, "context.json")
        self._ensure_data_directory()
        logger.info(f"Data Manager initialized with directory: {data_dir}")
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def store_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Store an interaction in the data store."""
        try:
            # Add metadata
            interaction_data["id"] = self._generate_interaction_id()
            interaction_data["stored_at"] = datetime.now().isoformat()
            
            # Append to interactions file
            with open(self.interactions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(interaction_data) + "\n")
            
            logger.info(f"Stored interaction with ID: {interaction_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            return False
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interactions."""
        try:
            interactions = []
            if os.path.exists(self.interactions_file):
                with open(self.interactions_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Get the last 'limit' lines
                    for line in lines[-limit:]:
                        if line.strip():
                            interactions.append(json.loads(line.strip()))
            
            logger.info(f"Retrieved {len(interactions)} recent interactions")
            return interactions
            
        except Exception as e:
            logger.error(f"Error retrieving recent interactions: {e}")
            return []
    
    def get_relevant_context(self, user_input: str, max_context: int = 5) -> Dict[str, Any]:
        """Get relevant context based on user input."""
        try:
            # Simple keyword-based relevance for now
            # In a more sophisticated system, this could use embeddings
            keywords = user_input.lower().split()
            relevant_interactions = []
            
            recent_interactions = self.get_recent_interactions(limit=50)
            
            for interaction in recent_interactions:
                # Check if any keywords match the interaction
                interaction_text = (
                    interaction.get("user_input", "") + " " + 
                    str(interaction.get("agent_responses", {}))
                ).lower()
                
                relevance_score = sum(1 for keyword in keywords if keyword in interaction_text)
                
                if relevance_score > 0:
                    interaction["relevance_score"] = relevance_score
                    relevant_interactions.append(interaction)
            
            # Sort by relevance and take top results
            relevant_interactions.sort(key=lambda x: x["relevance_score"], reverse=True)
            relevant_interactions = relevant_interactions[:max_context]
            
            context = {
                "relevant_interactions": relevant_interactions,
                "context_count": len(relevant_interactions),
                "search_keywords": keywords
            }
            
            logger.info(f"Found {len(relevant_interactions)} relevant interactions")
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return {"relevant_interactions": [], "context_count": 0, "search_keywords": []}
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get statistics about stored interactions."""
        try:
            stats = {
                "total_interactions": 0,
                "task_type_distribution": {},
                "agent_usage": {},
                "recent_activity": 0
            }
            
            if os.path.exists(self.interactions_file):
                with open(self.interactions_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    stats["total_interactions"] = len(lines)
                    
                    # Analyze last 24 hours
                    yesterday = datetime.now() - timedelta(days=1)
                    
                    for line in lines:
                        if line.strip():
                            interaction = json.loads(line.strip())
                            
                            # Task type distribution
                            task_type = interaction.get("task_type", "unknown")
                            stats["task_type_distribution"][task_type] = (
                                stats["task_type_distribution"].get(task_type, 0) + 1
                            )
                            
                            # Agent usage
                            agent_responses = interaction.get("agent_responses", {})
                            for agent_name in agent_responses.keys():
                                stats["agent_usage"][agent_name] = (
                                    stats["agent_usage"].get(agent_name, 0) + 1
                                )
                            
                            # Recent activity
                            if "timestamp" in interaction:
                                try:
                                    timestamp = datetime.fromisoformat(interaction["timestamp"])
                                    if timestamp > yesterday:
                                        stats["recent_activity"] += 1
                                except:
                                    pass
            
            logger.info("Generated interaction statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating interaction stats: {e}")
            return {"total_interactions": 0, "task_type_distribution": {}, "agent_usage": {}, "recent_activity": 0}
    
    def save_context(self, context_data: Dict[str, Any]) -> bool:
        """Save persistent context data."""
        try:
            with open(self.context_file, "w", encoding="utf-8") as f:
                json.dump(context_data, f, indent=2)
            
            logger.info("Saved context data")
            return True
            
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            return False
    
    def load_context(self) -> Dict[str, Any]:
        """Load persistent context data."""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, "r", encoding="utf-8") as f:
                    context = json.load(f)
                logger.info("Loaded context data")
                return context
            else:
                logger.info("No existing context file found")
                return {}
                
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old interaction data."""
        try:
            if not os.path.exists(self.interactions_file):
                return True
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            temp_file = self.interactions_file + ".temp"
            kept_count = 0
            
            with open(self.interactions_file, "r", encoding="utf-8") as infile, \
                 open(temp_file, "w", encoding="utf-8") as outfile:
                
                for line in infile:
                    if line.strip():
                        interaction = json.loads(line.strip())
                        if "timestamp" in interaction:
                            try:
                                timestamp = datetime.fromisoformat(interaction["timestamp"])
                                if timestamp > cutoff_date:
                                    outfile.write(line)
                                    kept_count += 1
                            except:
                                # Keep lines with invalid timestamps
                                outfile.write(line)
                                kept_count += 1
                        else:
                            # Keep lines without timestamps
                            outfile.write(line)
                            kept_count += 1
            
            # Replace original file with cleaned version
            os.replace(temp_file, self.interactions_file)
            
            logger.info(f"Cleaned up old data, kept {kept_count} interactions")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
    
    def _generate_interaction_id(self) -> str:
        """Generate a unique interaction ID."""
        from uuid import uuid4
        return str(uuid4())
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the data manager."""
        stats = self.get_interaction_stats()
        return {
            "status": "active",
            "data_directory": self.data_dir,
            "interactions_file": self.interactions_file,
            "context_file": self.context_file,
            "total_interactions": stats["total_interactions"],
            "recent_activity": stats["recent_activity"]
        }
