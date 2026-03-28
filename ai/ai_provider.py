"""
AI 提供方抽象基类和实现
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import sys

from config import (
    AI_PROVIDER,
    OLLAMA_URL,
    OLLAMA_MODEL,
    LMSTUDIO_URL,
    LOCAL_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_API_BASE,
)


@dataclass
class AIResponse:
    """AI 响应"""
    content: str
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AIProvider(ABC):
    """AI 提供方基类"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查 AI 提供方是否可用"""
        pass
    
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> AIResponse:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供方名称"""
        pass


class DummyProvider(AIProvider):
    """无 AI 提供方（默认）"""
    
    def is_available(self) -> bool:
        return True
    
    def chat(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> AIResponse:
        return AIResponse(
            content="AI 功能未启用。请在 .env 文件中配置 AI_PROVIDER。",
            success=False,
            error="AI_PROVIDER 未配置"
        )
    
    def get_provider_name(self) -> str:
        return "none"


class OpenAICompatibleProvider(AIProvider):
    """OpenAI 兼容 API 提供方"""
    
    def __init__(self, base_url: str, model: str, api_key: str = "dummy", provider_name: str = "openai-compatible"):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.provider_name = provider_name
    
    def is_available(self) -> bool:
        try:
            import requests
            # 简单检查连接
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code in [200, 401, 404]
        except:
            return False
    
    def chat(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> AIResponse:
        try:
            import requests
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({"role": "user", "content": f"参考信息：\n{context}"})
            
            messages.append({"role": "user", "content": user_prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            return AIResponse(
                content=content,
                success=True,
                metadata={"model": self.model, "provider": self.provider_name}
            )
        
        except Exception as e:
            return AIResponse(
                content="",
                success=False,
                error=str(e)
            )
    
    def get_provider_name(self) -> str:
        return self.provider_name


class OllamaProvider(OpenAICompatibleProvider):
    """Ollama 提供方"""
    
    def __init__(self):
        super().__init__(
            base_url=f"{OLLAMA_URL}/v1",
            model=OLLAMA_MODEL,
            api_key="ollama",
            provider_name="ollama"
        )
    
    def is_available(self) -> bool:
        try:
            import requests
            response = requests.get(OLLAMA_URL, timeout=2)
            return response.status_code in [200, 404]
        except:
            return False


class LMStudioProvider(OpenAICompatibleProvider):
    """LM Studio 提供方"""
    
    def __init__(self):
        super().__init__(
            base_url=LMSTUDIO_URL,
            model="local-model",
            api_key="lmstudio",
            provider_name="lmstudio"
        )


class LocalProvider(AIProvider):
    """本地 Transformers 提供方"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = LOCAL_MODEL
    
    def is_available(self) -> bool:
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            return True
        except ImportError:
            return False
    
    def _load_model(self):
        if self.model is None:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            print(f"正在加载本地模型: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            print("本地模型加载完成")
    
    def chat(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> AIResponse:
        try:
            self._load_model()
            
            prompt = f"{system_prompt}\n\n"
            if context:
                prompt += f"参考信息：\n{context}\n\n"
            prompt += f"用户问题：{user_prompt}\n\n回答："
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # 只取生成的部分
            response = response[len(prompt):]
            
            return AIResponse(
                content=response,
                success=True,
                metadata={"model": self.model_name, "provider": "local"}
            )
        
        except Exception as e:
            return AIResponse(
                content="",
                success=False,
                error=str(e)
            )
    
    def get_provider_name(self) -> str:
        return "local"


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI API 提供方"""
    
    def __init__(self):
        super().__init__(
            base_url=OPENAI_API_BASE,
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            provider_name="openai"
        )
    
    def is_available(self) -> bool:
        return bool(OPENAI_API_KEY)


def get_ai_provider() -> AIProvider:
    """获取 AI 提供方实例"""
    provider_name = AI_PROVIDER.lower()
    
    providers = {
        "none": DummyProvider,
        "ollama": OllamaProvider,
        "lmstudio": LMStudioProvider,
        "local": LocalProvider,
        "openai": OpenAIProvider,
    }
    
    provider_class = providers.get(provider_name, DummyProvider)
    provider = provider_class()
    
    # 检查是否可用
    if not provider.is_available() and provider_name != "none":
        print(f"警告: {provider_name} AI 提供方不可用，将使用无 AI 模式")
        return DummyProvider()
    
    return provider
