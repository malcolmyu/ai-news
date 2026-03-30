"""
Thinking-System Agent - Systematic thinking model management.

This agent provides capabilities for:
- Creating and managing structured thinking models
- Analyzing concept relationships
- Generating knowledge graphs
- Tracking model evolution
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import re
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Concept:
    """Represents a concept in the thinking model."""
    name: str
    description: str
    tags: List[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Relationship:
    """Represents a relationship between concepts."""
    from_concept: str
    to_concept: str
    type: str
    strength: float
    description: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Example:
    """Represents an example in the thinking model."""
    title: str
    description: str
    concepts: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ThinkingSystemAgent:
    """
    Agent for managing thinking models and knowledge structures.

    Provides capabilities for:
    - Creating systematic thinking models from content
    - Extracting structured data (concepts, relationships, examples)
    - Analyzing concept relationships
    - Generating knowledge graphs (using mermaid)
    - Managing model versions and evolution
    """

    def __init__(self, harness):
        """
        Initialize ThinkingSystemAgent.

        Args:
            harness: HarnessController instance for validation and templating
        """
        self.harness = harness
        self.models_dir = Path("data/thinking")
        self._ensure_data_structure()

        logger.info("ThinkingSystemAgent initialized")

    def _ensure_data_structure(self):
        """Ensure data directory structure exists."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        (self.models_dir / "relationships").mkdir(exist_ok=True)
        (self.models_dir / "versions").mkdir(exist_ok=True)

        # Create models index if not exists
        index_file = self.models_dir / "models.json"
        if not index_file.exists():
            self._save_json(index_file, {"models": [], "tags": {}})

    def _generate_id(self, topic: str) -> str:
        """Generate unique model ID from topic."""
        # Clean topic and create hash
        clean_topic = re.sub(r'[^\w\s]', '', topic.lower()).replace(' ', '_')
        hash_str = hashlib.md5(f"{clean_topic}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        return f"{clean_topic}_{hash_str}"

    def _get_current_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().isoformat()

    def _save_json(self, file_path: Path, data: Dict):
        """Save data to JSON file with formatting."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_json(self, file_path: Path) -> Dict:
        """Load data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_thinking_model(self, topic: str, content: str,
                            model_type: str = "framework") -> Dict[str, Any]:
        """
        Create a complete thinking model from topic and content.

        Args:
            topic: Main topic of the thinking model
            content: Content containing concepts, relationships, and examples
            model_type: Type of model (framework, methodology, pattern, etc.)

        Returns:
            Dictionary containing rendered HTML, structure, and graph data
        """
        logger.info(f"Creating thinking model for topic: {topic}")

        # Step 1: Extract structure from content
        structure = self.extract_structure(content, topic)

        # Step 2: Analyze relationships between concepts
        relationships = self.analyze_relationships(structure)

        # Step 3: Generate knowledge graph
        graph = self.generate_graph(structure, relationships)

        # Step 4: Create model with metadata
        from dataclasses import asdict
        model_data = {
            "id": self._generate_id(topic),
            "topic": topic,
            "version": "1.0",
            "model_type": model_type,
            "concepts": [asdict(c) for c in structure["concepts"]],
            "relationships": [asdict(r) for r in relationships],
            "examples": [asdict(e) for e in structure["examples"]],
            "references": structure.get("references", []),
            "created_at": self._get_current_date(),
            "updated_at": self._get_current_date()
        }

        # Step 5: Validate through Harness
        validation_result = self.harness.validate_thinking_model(content)

        if validation_result.score < 0.5:
            logger.warning(f"Thinking model has low quality score: {validation_result.score}")

        # Step 6: Apply template to generate HTML
        render_data = {
            "model": model_data,
            "structure": structure,
            "relationships": relationships,
            "graph": graph,
            "validation": {
                "is_valid": validation_result.is_valid,
                "score": validation_result.score,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            }
        }

        html = self.harness.apply_template("thinking_model", render_data)

        # Step 7: Save model data
        self.save_model(model_data)

        logger.info(f"Thinking model created successfully: {model_data['id']}")

        return {
            "html": html,
            "structure": structure,
            "graph": graph,
            "model": model_data,
            "validation": {
                "is_valid": validation_result.is_valid,
                "score": validation_result.score,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            }
        }

    def extract_structure(self, content: str, topic: str = "") -> Dict[str, Any]:
        """
        Extract structured data from content.

        Args:
            content: The content to analyze
            topic: Optional topic for context

        Returns:
            Dictionary with concepts, relationships, and examples
        """
        logger.info("Extracting structure from content")

        current_time = self._get_current_date()

        # Extract main concepts using simple NLP
        concepts = self._extract_concepts(content, topic, current_time)

        # Extract examples
        examples = self._extract_examples(content, current_time)

        # Extract references
        references = self._extract_references(content)

        structure = {
            "concepts": concepts,
            "examples": examples,
            "references": references
        }

        logger.info(f"Extracted {len(concepts)} concepts, {len(examples)} examples")

        return structure

    def _extract_concepts(self, content: str, topic: str, current_time: str) -> List[Concept]:
        """Extract concepts from content."""
        concepts = []
        seen_concepts = set()

        # Pattern 1: Look for bold terms (markdown)
        bold_pattern = r'\*\*([^*\n]+)\*\*|__([^_\n]+)__'
        for match in re.finditer(bold_pattern, content):
            concept_name = match.group(1) or match.group(2)
            if len(concept_name) > 1 and concept_name not in seen_concepts:
                description = self._get_context_around(content, match.start(), 50)
                concept = Concept(
                    name=concept_name.strip(),
                    description=description,
                    tags=self._extract_tags(concept_name, topic),
                    created_at=current_time,
                    updated_at=current_time
                )
                concepts.append(concept)
                seen_concepts.add(concept_name)

        # Pattern 2: Look for title case words that look like concepts
        title_pattern = r'[A-Z][a-z]+\s+(?:[A-Z][a-z]+\s*){0,2}'
        for match in re.finditer(title_pattern, content):
            concept_name = match.group().strip()
            if (len(concept_name.split()) <= 3 and
                len(concept_name) > 3 and
                concept_name not in seen_concepts):
                description = self._get_context_around(content, match.start(), 50)
                concept = Concept(
                    name=concept_name,
                    description=description,
                    tags=self._extract_tags(concept_name, topic),
                    created_at=current_time,
                    updated_at=current_time
                )
                concepts.append(concept)
                seen_concepts.add(concept_name)

        # If no concepts found, create one from the topic
        if not concepts:
            concept = Concept(
                name=topic or "Primary Concept",
                description="Main concept of the thinking model",
                tags=[topic.lower().replace(' ', '_') if topic else 'general'],
                created_at=current_time,
                updated_at=current_time
            )
            concepts.append(concept)

        return concepts

    def _extract_examples(self, content: str, current_time: str) -> List[Example]:
        """Extract examples from content."""
        examples = []

        # Pattern: Look for example headings
        example_patterns = [
            r'###\s*Example\s*([^\n]*)',
            r'###\s*示例\s*([^\n]*)',
            r'####\s*(.*?)(?:Example|示例)',
            r'(?:Example|示例)\s*:\s*([^\n]+)'
        ]

        concept_names = []
        for line in content.split('\n'):
            for pattern in example_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    title = match.group(1).strip() or f"Example {len(examples) + 1}"

                    # Extract description (next paragraph or lines)
                    start_idx = content.find(line) + len(line)
                    next_section = content[start_idx:]
                    next_newline = next_section.find('\n\n')
                    if next_newline > 0:
                        description = next_section[:next_newline].strip()
                    else:
                        description = next_section[:200].strip()

                    example = Example(
                        title=title,
                        description=description,
                        concepts=concept_names[:5],  # Link to recently found concepts
                        created_at=current_time
                    )
                    examples.append(example)
                    break

        # If no explicit examples, create one from the first paragraph
        if not examples:
            paragraphs = content.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0].strip()
                if len(first_para) > 50:
                    example = Example(
                        title="Usage Context",
                        description=first_para[:200] + "...",
                        concepts=[],
                        created_at=current_time
                    )
                    examples.append(example)

        return examples

    def _extract_tags(self, concept_name: str, topic: str) -> List[str]:
        """Extract tags for a concept."""
        tags = []

        # Add topic-based tag
        if topic:
            topic_tag = topic.lower().replace(' ', '_')
            tags.append(topic_tag)

        # Add concept name components
        words = concept_name.lower().split()
        tags.extend(words[:3])  # Use first 3 words as tags

        # Remove duplicates
        return list(set(tags))

    def _get_context_around(self, content: str, position: int, radius: int) -> str:
        """Get text context around a position."""
        start = max(0, position - radius)
        end = min(len(content), position + radius)
        return content[start:end].strip()

    def _extract_references(self, content: str) -> List[str]:
        """Extract references from content."""
        references = []

        # Pattern: Look for reference patterns
        reference_patterns = [
            r'\[([^\]]+)\]\(http[^)]+\)',
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'[A-Z][a-z]+\s+et\.?\s+al\.',
            r'\d{4}\s*[,;]?\s*[A-Z][a-z]+'
        ]

        for pattern in reference_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)

        return list(set(references))[:10]  # Limit to 10 references

    def analyze_relationships(self, structure: Dict[str, Any]) -> List[Relationship]:
        """
        Analyze relationships between concepts.

        Args:
            structure: Extracted structure containing concepts

        Returns:
            List of relationships between concepts
        """
        logger.info("Analyzing relationships between concepts")

        concepts = structure.get("concepts", [])
        relationships = []
        seen_pairs = set()
        current_time = self._get_current_date()

        if not concepts:
            return relationships

        # Analyze relationships between concept pairs
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts):
                if i >= j:  # Skip self and duplicates
                    continue

                pair_key = tuple(sorted([concept1.name, concept2.name]))
                if pair_key in seen_pairs:
                    continue

                relationship_type, strength = self._determine_relationship(concept1, concept2)

                relationship = Relationship(
                    from_concept=concept1.name,
                    to_concept=concept2.name,
                    type=relationship_type,
                    strength=strength,
                    description=f"{concept1.name} {relationship_type.replace('_', ' ')} {concept2.name}",
                    created_at=current_time
                )
                relationships.append(relationship)
                seen_pairs.add(pair_key)

        # Add hierarchical relationships if we have a clear hierarchy
        if len(concepts) >= 3:
            relationships.extend(self._add_hierarchical_relationships(concepts, current_time))

        logger.info(f"Found {len(relationships)} relationships")

        return relationships

    def _determine_relationship(self, concept1: Concept, concept2: Concept) -> Tuple[str, float]:
        """
        Determine relationship type and strength between two concepts.

        Args:
            concept1: First concept
            concept2: Second concept

        Returns:
            Tuple of (relationship_type, strength)
        """
        # Check for shared tags
        shared_tags = set(concept1.tags) & set(concept2.tags)

        # Default relationship based on shared concepts
        if len(shared_tags) >= 2:
            return "closely_related", 0.8
        elif len(shared_tags) >= 1:
            return "related_to", 0.6
        else:
            # Check for semantic relationships
            name1 = concept1.name.lower()
            name2 = concept2.name.lower()

            if "framework" in name1 or "framework" in name2:
                return "part_of_framework", 0.7
            elif "process" in name1 or "process" in name2:
                return "part_of_process", 0.6
            elif "model" in name1 or "model" in name2:
                return "model_component", 0.5
            else:
                return "related_to", 0.4

    def _add_hierarchical_relationships(self, concepts: List[Concept],
                                       current_time: str) -> List[Relationship]:
        """Add hierarchical relationships based on concept names."""
        relationships = []

        # Find potential parent concepts (shorter, more general names)
        potential_parents = [
            c for c in concepts
            if len(c.name.split()) <= 2 and len(c.name) > 3
        ]

        if not potential_parents:
            return relationships

        parent = potential_parents[0]  # Use first as parent

        # Create is_a or part_of relationships to parent
        for concept in concepts[1:10]:  # Limit to prevent too many relationships
            if concept.name != parent.name:
                rel_type = "part_of" if "process" in parent.name.lower() else "is_a"
                relationship = Relationship(
                    from_concept=concept.name,
                    to_concept=parent.name,
                    type=rel_type,
                    strength=0.5,
                    description=f"{concept.name} {rel_type.replace('_', ' ')} {parent.name}",
                    created_at=current_time
                )
                relationships.append(relationship)

        return relationships

    def generate_graph(self, structure: Dict[str, Any],
                      relationships: List[Relationship]) -> str:
        """
        Generate knowledge graph using mermaid syntax.

        Args:
            structure: Extracted structure with concepts
            relationships: Analyzed relationships

        Returns:
            Mermaid graph definition string
        """
        logger.info("Generating knowledge graph")

        concepts = structure.get("concepts", [])

        if not concepts:
            return "graph TD\n  Empty[No concepts found]"

        # Start mermaid graph
        graph_lines = ["graph TD"]

        # Add concept nodes
        for concept in concepts:
            escaped_name = self._escape_mermaid_id(concept.name)
            # Add color based on tags or strength
            fill_color = self._get_node_color(concept.tags)
            graph_lines.append(
                f'  {escaped_name}["{concept.name}"]:::concept'
            )

        # Add relationships as edges
        for rel in relationships[:15]:  # Limit to prevent overcrowding
            from_node = self._escape_mermaid_id(rel.from_concept)
            to_node = self._escape_mermaid_id(rel.to_concept)

            # Determine edge style based on strength
            edge_style = self._get_edge_style(rel.strength, rel.type)

            graph_lines.append(
                f'  {from_node} {edge_style} {to_node}'
            )

        # Add styling
        graph_lines.extend([
            "classDef concept fill:#f9f9f9,stroke:#333,stroke-width:2px;",
            "classDef highlight fill:#e1f5fe,stroke:#006064;",
            "classDef important fill:#fff3e0,stroke:#e65100;"
        ])

        logger.info(f"Generated graph with {len(concepts)} nodes and {len(relationships)} edges")

        return "\n".join(graph_lines)

    def _escape_mermaid_id(self, name: str) -> str:
        """Escape name for mermaid ID."""
        # Replace spaces with underscore, remove special chars
        return re.sub(r'[^\w]', '_', name.strip()).lower()

    def _get_node_color(self, tags: List[str]) -> str:
        """Get node color based on tags."""
        # Simple color mapping based on tags
        color_map = {
            'framework': '#e1f5fe',
            'process': '#f3e5f5',
            'model': '#e8f5e9',
            'decision': '#fff9c4'
        }

        for tag in tags:
            if tag in color_map:
                return color_map[tag]

        return '#f9f9f9'  # Default

    def _get_edge_style(self, strength: float, rel_type: str) -> str:
        """Get edge style based on relationship strength and type."""
        if strength >= 0.8:
            return f'-- {rel_type.replace("_", " ")} -->'
        elif strength >= 0.6:
            return f'-. {rel_type.replace("_", " ")} .->'
        else:
            return f'-.->'

    def save_model(self, model_data: Dict[str, Any]) -> bool:
        """
        Save thinking model to data store.

        Args:
            model_data: Model data to save

        Returns:
            True if successful
        """
        try:
            model_id = model_data['id']

            # Save model to versions
            version_file = self.models_dir / "versions" / f"{model_id}_v1.0.json"
            self._save_json(version_file, model_data)

            # Update relationships
            rel_file = self.models_dir / "relationships" / f"{model_id}.json"
            self._save_json(rel_file, {
                "model_id": model_id,
                "relationships": model_data['relationships'],
                "created_at": model_data['created_at']
            })

            self._update_model_index(model_data)

            logger.info(f"Model saved: {model_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def _update_model_index(self, model_data: Dict[str, Any]):
        """Update the models index file."""
        index_file = self.models_dir / "models.json"
        index_data = self._load_json(index_file)

        # Update models list
        existing_idx = next((i for i, m in enumerate(index_data['models'])
                           if m['id'] == model_data['id']), None)

        model_summary = {
            "id": model_data['id'],
            "topic": model_data['topic'],
            "version": model_data['version'],
            "model_type": model_data['model_type'],
            "created_at": model_data['created_at'],
            "updated_at": model_data['updated_at']
        }

        if existing_idx is not None:
            index_data['models'][existing_idx] = model_summary
        else:
            index_data['models'].append(model_summary)

        # Update tags index
        for concept in model_data['concepts']:
            for tag in concept.get('tags', []):
                if tag not in index_data['tags']:
                    index_data['tags'][tag] = []
                if model_data['id'] not in index_data['tags'][tag]:
                    index_data['tags'][tag].append(model_data['id'])

        self._save_json(index_file, index_data)

    def update_model(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing model and create new version.

        Args:
            model_id: ID of model to update
            updates: Updates to apply

        Returns:
            True if update successful
        """
        try:
            # Load current version
            version_file = self.models_dir / "versions" / f"{model_id}_v1.0.json"
            if not version_file.exists():
                logger.error(f"Model not found: {model_id}")
                return False

            model_data = self._load_json(version_file)

            # Determine new version number
            current_version = model_data['version']
            major, minor = map(int, current_version.split('.'))
            new_version = f"{major}.{minor + 1}"

            # Apply updates
            model_data.update(updates)
            model_data['version'] = new_version
            model_data['updated_at'] = self._get_current_date()

            # Save new version
            new_version_file = self.models_dir / "versions" / f"{model_id}_{new_version}.json"
            self._save_json(new_version_file, model_data)

            # Update relationships
            rel_file = self.models_dir / "relationships" / f"{model_id}.json"
            if 'relationships' in updates:
                rel_data = self._load_json(rel_file)
                rel_data['relationships'] = updates['relationships']
                rel_data['updated_at'] = model_data['updated_at']
                self._save_json(rel_file, rel_data)

            self._update_model_index(model_data)

            logger.info(f"Model updated: {model_id} -> v{new_version}")
            return True

        except Exception as e:
            logger.error(f"Failed to update model: {e}")
            return False

    def find_related_models(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Find related models based on tags and concepts.

        Args:
            model_id: ID of model to find relations for

        Returns:
            List of related models
        """
        try:
            # Load target model
            version_file = self.models_dir / "versions" / f"{model_id}_v1.0.json"
            if not version_file.exists():
                return []

            target_model = self._load_json(version_file)
            target_tags = set()
            for concept in target_model['concepts']:
                target_tags.update(concept.get('tags', []))

            # Load index
            index_file = self.models_dir / "models.json"
            index_data = self._load_json(index_file)

            related_models = []
            seen_ids = {model_id}

            for tag in target_tags:
                model_ids = index_data['tags'].get(tag, [])
                for related_id in model_ids:
                    if related_id in seen_ids:
                        continue

                    related_file = self.models_dir / "versions" / f"{related_id}_v1.0.json"
                    if related_file.exists():
                        model_data = self._load_json(related_file)
                        related_models.append({
                            "id": related_id,
                            "topic": model_data['topic'],
                            "model_type": model_data['model_type'],
                            "shared_tags": [tag],
                            "similarity": 0.7
                        })
                        seen_ids.add(related_id)

            logger.info(f"Found {len(related_models)} related models for {model_id}")
            return related_models

        except Exception as e:
            logger.error(f"Error finding related models: {e}")
            return []

    def get_model_index(self) -> Dict[str, Any]:
        """Get the model index."""
        index_file = self.models_dir / "models.json"
        return self._load_json(index_file)
