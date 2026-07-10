import re
import time
import inspect
from typing import List, Optional
from embodied_ai import EmbodiedAI




# ──────────────────────────────────────────────
# Mapeamento automático dos métodos do EmbodiedAI
# ──────────────────────────────────────────────
ACTION_MAP = {
   name.replace("_", " "): name
   for name, _ in inspect.getmembers(EmbodiedAI, predicate=inspect.isfunction)
   if not name.startswith("_")
}


CLASS_ALIASES = {
   "person":     "person",
   "people":     "person",
   "human":      "person",
   "chair":      "chair",
   "table":      "table",
   "bottle":     "bottle",
   "dog":        "dog",
   "cat":        "cat",
   "laptop":     "laptop",
   "phone":      "cell phone",
   "cell phone": "cell phone",
}


OPERATOR_MAP = {
   "closer than":     "<",
   "less than":       "<",
   "within":          "<",
   "nearer than":     "<",
   "farther than":    ">",
   "further than":    ">",
   "more than":       ">",
   "beyond":          ">",
   "at least":        ">=",
   "no closer than":  ">=",
   "at most":         "<=",
   "no farther than": "<=",
}




# ──────────────────────────────────────────────
# Rule — uso interno
# ──────────────────────────────────────────────
class Rule:
   """
   Parseia uma regra do tipo:
       <action> if [you detect/see] <class> [operator] <distance> meter(s)


   Exemplos:
       "shake hand if person is within 1.0 meters"
       "reject if you detect a person closer than 0.5 meters"
       "hands up if person is farther than 1.5 meters"
       "clap if chair"
       "wave hand if human is closer than 2 meters"
   """


   def __init__(self, raw: str):
       self.raw            = raw.strip().lower()
       self.action_method: Optional[str]   = None
       self.target_class:  Optional[str]   = None
       self.operator:      Optional[str]   = None
       self.threshold:     Optional[float] = None
       self._parse()


   def _parse(self):
       text = self.raw


       if " if " not in text:
           raise ValueError(f"Regra inválida (sem 'if'): '{self.raw}'")


       action_part, condition_part = text.split(" if ", 1)
       action_part    = action_part.strip()
       condition_part = condition_part.strip()


       for noise in ["you detect", "you see", "there is", "a ", "an ", "is ", "are "]:
           condition_part = condition_part.replace(noise, " ")
       condition_part = " ".join(condition_part.split())


       self.action_method = self._parse_action(action_part)
       self.target_class  = self._parse_class(condition_part)
       self._parse_distance(condition_part)


   def _parse_action(self, action_part: str) -> str:
       if action_part in ACTION_MAP:
           return ACTION_MAP[action_part]
       for key in sorted(ACTION_MAP, key=len, reverse=True):
           if key in action_part:
               return ACTION_MAP[key]
       available = ", ".join(sorted(ACTION_MAP.keys()))
       raise ValueError(
           f"Ação '{action_part}' não reconhecida.\n"
           f"Disponíveis: {available}"
       )


   def _parse_class(self, condition_part: str) -> str:
       for alias, canonical in CLASS_ALIASES.items():
           if alias in condition_part:
               return canonical
       raise ValueError(
           f"Classe não reconhecida em: '{condition_part}'\n"
           f"Disponíveis: {', '.join(CLASS_ALIASES.keys())}"
       )


   def _parse_distance(self, condition_part: str) -> None:
       for op_str, op_sym in sorted(OPERATOR_MAP.items(), key=lambda kv: len(kv[0]), reverse=True):
           if op_str in condition_part:
               after = condition_part.split(op_str, 1)[1]
               numbers = re.findall(r"\d+(?:\.\d+)?", after)
               if numbers:
                   self.operator = op_sym
                   self.threshold = float(numbers[0])
                   return


   def evaluate(self, detections: List[dict]) -> bool:
       """Retorna True se alguma detecção satisfaz a condição da regra."""
       for d in detections:
           if d["class"] != self.target_class:
               continue
           if self.operator is None:
               return True
           dist = d.get("distance_m", 0.0)
           if dist <= 0.0:
               continue
           if self.operator == "<"  and dist <  self.threshold: return True
           if self.operator == ">"  and dist >  self.threshold: return True
           if self.operator == "<=" and dist <= self.threshold: return True
           if self.operator == ">=" and dist >= self.threshold: return True
       return False


   def __repr__(self):
       dist_str = (
           f"{self.operator} {self.threshold}m"
           if self.operator else "any distance"
       )
       return f"Rule('{self.action_method}' if '{self.target_class}' {dist_str})"




# ──────────────────────────────────────────────
# BehaviorEngine — uso externo
# ──────────────────────────────────────────────
class BehaviorEngine(EmbodiedAI):
   """
   Motor de comportamento reativo sobre EmbodiedAI.
   Interpreta regras em linguagem natural e executa
   qualquer método público do EmbodiedAI como ação.


   Uso:
       robot = BehaviorEngine("eth0")
       robot.load("shake hand if person is within 1.0 meters")
       robot.run()
   """


   def __init__(
       self,
       network_interface: str,
       loop_interval: float = 1.0,
       cooldown: float = 3.0,
       **kwargs,
   ):
       super().__init__(network_interface, **kwargs)
       self._rules:      List[Rule] = []
       self._loop_interval          = loop_interval
       self._cooldown               = cooldown
       self._last_fired: dict       = {}


   def load(self, rule_string: str) -> None:
       """
       Parseia e registra uma regra em linguagem natural.


       Args:
           rule_string: Ex: "shake hand if person is within 1.0 meters"
       """
       rule = Rule(rule_string)
       self._rules.append(rule)
       self._last_fired[id(rule)] = 0.0
       print(f"[BehaviorEngine] Regra carregada: {rule}")


   def load_many(self, rules: List[str]) -> None:
       """Carrega múltiplas regras de uma lista de strings."""
       for r in rules:
           self.load(r)


   def clear_rules(self) -> None:
       """Remove todas as regras carregadas."""
       self._rules.clear()
       self._last_fired.clear()
       print("[BehaviorEngine] Regras removidas.")


   def available_actions(self) -> List[str]:
       """Lista todas as ações disponíveis."""
       return sorted(ACTION_MAP.keys())


   def available_classes(self) -> List[str]:
       """Lista todas as classes de objetos reconhecidas."""
       return sorted(CLASS_ALIASES.keys())


   def step(self) -> None:
       """Executa um ciclo: captura detecções e avalia todas as regras."""
       detections = self.detect_with_distance()
       now        = time.time()


       for rule in self._rules:
           if not rule.evaluate(detections):
               continue
           elapsed = now - self._last_fired[id(rule)]
           if elapsed < self._cooldown:
               continue
           action_fn = getattr(self, rule.action_method, None)
           if action_fn:
               print(
                   f"[BehaviorEngine] '{rule.action_method}' "
                   f"← '{rule.target_class}' detectado"
               )
               action_fn()
               self._last_fired[id(rule)] = now


   def run(self) -> None:
       """Loop principal — Ctrl+C para encerrar."""
       print(
           f"[BehaviorEngine] {len(self._rules)} regra(s) ativa(s). "
           f"Ctrl+C para parar."
       )
       try:
           while True:
               self.step()
               time.sleep(self._loop_interval)
       except KeyboardInterrupt:
           print("[BehaviorEngine] Encerrado.")
       finally:
           self.stop()
           self.close_camera()



