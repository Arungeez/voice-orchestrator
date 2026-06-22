import { useEffect, useRef, useCallback } from 'react'

/**
 * useWebSocket
 * Connects to /ws/updates?company_id=X and calls onMessage
 * whenever the server broadcasts a lead status update.
 * Auto-reconnects if the connection drops.
 */
export function useWebSocket(companyId, onMessage) {
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)
  const mountedRef = useRef(true)

  const connect = useCallback(() => {
    if (!companyId || !mountedRef.current) return

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.host
    const url = `${protocol}://${host}/ws/updates?company_id=${companyId}`

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        console.log(`🔌 WS connected for company ${companyId}`)
        // Clear any pending reconnect
        if (reconnectTimer.current) {
          clearTimeout(reconnectTimer.current)
          reconnectTimer.current = null
        }
        // Keep-alive ping every 25s
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping')
          } else {
            clearInterval(pingInterval)
          }
        }, 25000)
        ws._pingInterval = pingInterval
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessage) onMessage(data)
        } catch {
          // Not JSON — ignore
        }
      }

      ws.onclose = () => {
        if (ws._pingInterval) clearInterval(ws._pingInterval)
        if (mountedRef.current) {
          // Reconnect after 3 seconds
          reconnectTimer.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = (err) => {
        console.warn('WS error:', err)
        ws.close()
      }
    } catch (err) {
      console.warn('WS connect failed:', err)
    }
  }, [companyId, onMessage])

  useEffect(() => {
    mountedRef.current = true
    connect()

    return () => {
      mountedRef.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) {
        if (wsRef.current._pingInterval) clearInterval(wsRef.current._pingInterval)
        wsRef.current.close()
      }
    }
  }, [connect])
}
