import { useHistoryStore } from './modules/history'
import { useFavoriteStore } from './modules/favorite'

/** 切账号 / 退出时清掉内存里的历史和收藏，避免串到下一个用户 */
export function resetAccountCaches() {
  useHistoryStore().resetForAccountSwitch()
  useFavoriteStore().resetForAccountSwitch()
}
