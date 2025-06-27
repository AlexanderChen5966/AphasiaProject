<template>
  <div v-if="currentScene"
       :style="{ backgroundImage: 'url(' + currentScene.image + ')', backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat' }"
       class="relative min-h-screen flex flex-col items-center justify-between text-white p-4 transition-all duration-500 ease-in-out">

    <h1 class="text-3xl sm:text-4xl font-bold mt-8 text-yellow-200 text-center drop-shadow-lg"
        :style="{ fontFamily: 'NotoSansTC' }">
      {{ currentScene.title }}
    </h1>

    <div class="bg-black bg-opacity-70 rounded-lg p-6 max-w-4xl w-full mx-auto my-auto shadow-xl">
      <p v-if="currentScene.dialogue && currentScene.dialogue.length > 0" class="text-base sm:text-lg md:text-xl leading-relaxed" :style="{ fontFamily: 'NotoSansTC' }">
        {{ currentScene.dialogue[0] }}
      </p>
      <p v-if="currentScene.hint" class="mt-4 text-sm text-gray-300 italic" :style="{ fontFamily: 'NotoSansTC' }">
        {{ currentScene.hint }}
      </p>
      <p v-if="currentScene.extra_hint" class="mt-2 text-xs text-gray-400 italic" :style="{ fontFamily: 'NotoSansTC' }">
        {{ currentScene.extra_hint }}
      </p>
    </div>

    <div class="flex flex-col space-y-4 mb-8 w-full max-w-md px-4">
      <button v-for="trigger in currentScene.triggers" :key="trigger.next_id + trigger.pattern"
              @click="handleChoice(trigger.next_id, trigger.response, trigger.fx_sound, trigger.fx_image)"
              class="bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              :style="{ fontFamily: 'NotoSansTC' }"
              :disabled="isLoading">
        {{ trigger.pattern }}
      </button>
    </div>

    <audio ref="bgmAudio" :src="currentScene.sound" loop autoplay @error="handleAudioError"></audio>

    <audio ref="fxAudio"></audio>

    <div v-if="isLoading && !currentScene" class="absolute inset-0 flex justify-center items-center bg-gray-900 bg-opacity-80 text-white text-2xl" :style="{ fontFamily: 'NotoSansTC' }">
      載入故事中，請稍候...
    </div>
    <div v-if="errorMessage" class="absolute inset-0 flex justify-center items-center bg-red-900 bg-opacity-80 text-white text-xl p-4 text-center" :style="{ fontFamily: 'NotoSansTC' }">
      {{ errorMessage }}
      <button @click="resetGame" class="mt-4 bg-red-700 hover:bg-red-800 text-white py-2 px-4 rounded">重新開始</button>
    </div>
  </div>
  <div v-else-if="!errorMessage" class="flex justify-center items-center min-h-screen bg-gray-900 text-white text-2xl" :style="{ fontFamily: 'NotoSansTC' }">
    初始化故事...
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

// 創建一個獨立的 Axios 實例，確保 baseURL 正確且不會被其他地方干擾
const apiClient = axios.create({
  baseURL: 'https://aphasiaprojectapi.zeabur.app/api', // <-- 這裡包含了 /api
});

const currentScene = ref(null);
const bgmAudio = ref(null); // 用於引用 <audio> 元素 (背景音樂)
const fxAudio = ref(null); // 用於引用 <audio> 元素 (點擊音效)
const isLoading = ref(true); // 載入狀態
const errorMessage = ref(null); // 錯誤訊息

// 載入場景數據
const loadScene = async (id) => {
  console.log(`loadScene 函數被呼叫，嘗試載入 ID: ${id}`);
  isLoading.value = true;
  errorMessage.value = null; // 清除之前的錯誤訊息
  try {
    // 透過 apiClient 實例發送請求，只需提供相對路徑
    const requestUrl = `/scene/${id}`;
    // 新增日誌：記錄實際要發出的完整 URL
    console.log(`即將請求場景數據的完整 URL: ${apiClient.defaults.baseURL}${requestUrl}`);

    const response = await apiClient.get(requestUrl);
    console.log("成功從 API 獲取場景數據:", response.data);
    currentScene.value = response.data;
    console.log("載入的場景數據:", response.data);
    console.log("對話數據:", response.data.dialogue);

    // 處理背景音樂播放
    if (bgmAudio.value) {
      if (currentScene.value.sound) {
        bgmAudio.value.src = currentScene.value.sound; // 更新音源
        bgmAudio.value.load(); // 載入新音源
        try {
          await bgmAudio.value.play();
        } catch (e) {
          console.warn("背景音樂自動播放被瀏覽器阻止:", e);
          // 在這裡可以提示用戶手動播放音樂，例如一個小的音量按鈕
        }
      } else {
        bgmAudio.value.pause();
        bgmAudio.value.src = ''; // 沒有音樂則清空音源
      }
    }
  } catch (error) {
    console.error("載入場景錯誤:", error);
    currentScene.value = null; // 清空場景數據
    if (error.response && error.response.status === 404) {
      errorMessage.value = `場景數據未找到 (ID: ${id})。遊戲可能已結束或數據錯誤。請檢查後端日誌。`;
    } else {
      errorMessage.value = `無法連接到遊戲伺服器或發生其他錯誤: ${error.message}。請確認後端是否運行。`;
    }
  } finally {
    isLoading.value = false;
  }
};

// 處理玩家選擇
const handleChoice = async (nextId, responseText, fxSound, fxImage) => {
    // 先播放點擊音效 (如果有的話)
    if (fxAudio.value && fxSound) {
        // 假設音效路徑相對於前端根目錄
        fxAudio.value.src = `/assets/sounds/${fxSound}`;
        try {
            await fxAudio.value.play();
        } catch (e) {
            console.warn("點擊音效播放被阻止:", e);
        }
    }

    // 載入下一個場景
    await loadScene(nextId);
    // 如果需要顯示 responseText，可以在這裡加入一個訊息提示框或日誌
    // console.log("玩家選擇回應:", responseText);
};

// 處理音頻播放錯誤
const handleAudioError = (e) => {
  console.error("音頻播放錯誤 (可能是檔案不存在或格式不支援):", e);
  // 可以選擇顯示一個小圖標或訊息
};

// 重新開始遊戲
const resetGame = async () => {
  errorMessage.value = null;
  isLoading.value = true;
  try {
    console.log("開始獲取起始ID...");
    // 透過 apiClient 實例發送請求，只需提供相對路徑
    const requestUrl = `/start_id`;
    // 新增日誌：記錄實際要發出的完整 URL
    console.log(`即將請求起始ID的完整 URL: ${apiClient.defaults.baseURL}${requestUrl}`);

    const startIdResponse = await apiClient.get(requestUrl);
    console.log("成功獲取起始ID:", startIdResponse.data.start_id);

    console.log("準備載入場景數據，ID:", startIdResponse.data.start_id);
    await loadScene(startIdResponse.data.start_id);
    console.log("loadScene 執行完成。");
  } catch (error) {
    console.error("重新開始遊戲時獲取起始 ID 錯誤:", error);
    errorMessage.value = "無法重新開始遊戲，請檢查伺服器連線。";
  } finally {
    isLoading.value = false;
  }
};


// 組件掛載時，首先獲取起始 ID，然後載入第一個場景
onMounted(async () => {
  await resetGame(); // 使用 resetGame 來初始化，方便重複邏輯
});
</script>

<style scoped>
/* 這裡可以放 GameScene.vue 特有的樣式 */
.drop-shadow-lg {
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7); /* 更明顯的陰影 */
}
</style>
