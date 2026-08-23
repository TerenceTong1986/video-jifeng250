package com.livespeedtest

import android.app.Activity
import android.content.Intent
import android.graphics.Typeface
import android.net.Uri
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var tvFileName: TextView
    private lateinit var tvCount: TextView
    private lateinit var btnSelect: Button
    private lateinit var btnStart: Button
    private lateinit var btnExport: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var tvProgress: TextView
    private lateinit var resultContainer: LinearLayout

    private val sources = mutableListOf<String>()
    private val results = mutableListOf<SpeedTestResult>()
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    companion object {
        private const val FILE_SELECT_CODE = 1
        private const val FILE_EXPORT_CODE = 2
        private const val TIMEOUT_MS = 5000
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvFileName = findViewById(R.id.tvFileName)
        tvCount = findViewById(R.id.tvCount)
        btnSelect = findViewById(R.id.btnSelect)
        btnStart = findViewById(R.id.btnStart)
        btnExport = findViewById(R.id.btnExport)
        progressBar = findViewById(R.id.progressBar)
        tvProgress = findViewById(R.id.tvProgress)
        resultContainer = findViewById(R.id.resultContainer)

        btnSelect.setOnClickListener { selectFile() }
        btnStart.setOnClickListener { startSpeedTest() }
        btnExport.setOnClickListener { exportBest() }
    }

    private fun selectFile() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
        }
        startActivityForResult(intent, FILE_SELECT_CODE)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        when (requestCode) {
            FILE_SELECT_CODE -> {
                if (resultCode == Activity.RESULT_OK && data?.data != null) {
                    loadFile(data.data!!)
                }
            }
            FILE_EXPORT_CODE -> {
                if (resultCode == Activity.RESULT_OK && data?.data != null) {
                    exportResults(data.data!!)
                }
            }
        }
    }

    private fun loadFile(uri: Uri) {
        scope.launch {
            try {
                val inputStream = contentResolver.openInputStream(uri)
                val reader = BufferedReader(InputStreamReader(inputStream))
                val lines = reader.readLines()
                reader.close()

                sources.clear()
                var i = 0
                while (i < lines.size) {
                    val line = lines[i].trim()
                    when {
                        line.startsWith("#EXTINF:") -> {
                            i++
                            if (i < lines.size && lines[i].trim().startsWith("http")) {
                                sources.add(lines[i].trim())
                            }
                        }
                        line.startsWith("http") || line.startsWith("rtmp") || line.startsWith("rtsp") -> {
                            sources.add(line)
                        }
                    }
                    i++
                }

                val fileName = uri.lastPathSegment?.substringAfterLast('/') ?: "文件"
                tvFileName.text = "已选: $fileName"
                tvCount.text = "源数量: ${sources.size}"
                tvProgress.text = "准备就绪，点击开始测速"
                resultContainer.removeAllViews()
                results.clear()
                btnExport.isEnabled = false
                Toast.makeText(this@MainActivity, "已加载 ${sources.size} 个源", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "读取失败: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun startSpeedTest() {
        if (sources.isEmpty()) {
            Toast.makeText(this, "请先选择文件", Toast.LENGTH_SHORT).show()
            return
        }

        results.clear()
        resultContainer.removeAllViews()
        progressBar.max = sources.size
        progressBar.progress = 0
        btnStart.isEnabled = false
        btnStart.text = "⏳ 测速中..."
        btnExport.isEnabled = false

        scope.launch {
            val allResults = mutableListOf<SpeedTestResult>()
            val batchSize = 10
            var done = 0

            for (i in sources.indices step batchSize) {
                val batch = sources.subList(i, minOf(i + batchSize, sources.size))
                val deferred = batch.map { url ->
                    async(Dispatchers.IO) {
                        testUrl(url)
                    }
                }
                val batchResults = deferred.awaitAll()
                allResults.addAll(batchResults)
                done += batch.size

                withContext(Dispatchers.Main) {
                    progressBar.progress = done
                    tvProgress.text = "测速中: $done/${sources.size}"
                    val sorted = allResults.sortedWith(compareBy<SpeedTestResult> { !it.available }.thenBy { it.latency })
                    updateResultList(sorted)
                }
            }

            val sorted = allResults.sortedWith(compareBy<SpeedTestResult> { !it.available }.thenBy { it.latency })
            results.clear()
            results.addAll(sorted)

            val available = sorted.count { it.available }
            btnStart.isEnabled = true
            btnStart.text = "▶ 重新测速"
            btnExport.isEnabled = available > 0
            tvProgress.text = "✅ 完成！${available}/${sorted.size} 可用"
        }
    }

    private fun testUrl(urlString: String): SpeedTestResult {
        val start = System.currentTimeMillis()
        try {
            val url = URL(urlString)
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "HEAD"
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = TIMEOUT_MS
            connection.instanceFollowRedirects = true
            connection.connect()
            val code = connection.responseCode
            val latency = System.currentTimeMillis() - start
            connection.disconnect()
            return SpeedTestResult(urlString, true, latency, code)
        } catch (e: Exception) {
            val elapsed = System.currentTimeMillis() - start
            return SpeedTestResult(urlString, false, elapsed, 0, e.message ?: "未知错误")
        }
    }

    private fun updateResultList(sorted: List<SpeedTestResult>) {
        resultContainer.removeAllViews()
        val showCount = minOf(sorted.size, 200)
        for (i in 0 until showCount) {
            val r = sorted[i]
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    dpToPx(36)
                ).apply { setMargins(0, 1, 0, 0) }
                setPadding(dpToPx(8), dpToPx(4), dpToPx(8), dpToPx(4))
                setBackgroundColor(if (i % 2 == 0) 0x0DFFFFFF.toInt() else 0x00000000)
            }

            // Status icon
            val statusIcon = TextView(this).apply {
                val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                layoutParams = lp
                text = if (r.available) "✅" else "❌"
                textSize = 12f
            }
            row.addView(statusIcon)

            // URL
            val urlText = TextView(this).apply {
                val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 3f)
                layoutParams = lp
                text = r.url
                textSize = 10f
                textColor = 0xFFE6EDF3.toInt()
                maxLines = 1
                ellipsize = android.text.TextUtils.TruncateAt.MIDDLE
            }
            row.addView(urlText)

            // Latency
            val latencyText = TextView(this).apply {
                val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                lp.gravity = android.view.Gravity.END
                layoutParams = lp
                gravity = android.view.Gravity.END
                if (r.available) {
                    text = "${r.latency}ms"
                    textColor = if (r.latency < 200) 0xFF238636.toInt()
                    else if (r.latency < 500) 0xFFD29922.toInt()
                    else 0xFFF85149.toInt()
                } else {
                    text = "超时"
                    textColor = 0xFF484F58.toInt()
                }
                textSize = 11f
                typeface = Typeface.DEFAULT_BOLD
            }
            row.addView(latencyText)

            resultContainer.addView(row)
        }
        if (sorted.size > 200) {
            val more = TextView(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                text = "... 还有 ${sorted.size - 200} 个源"
                textSize = 11f
                textColor = 0xFF484F58.toInt()
                gravity = android.view.Gravity.CENTER
                setPadding(0, dpToPx(8), 0, dpToPx(8))
            }
            resultContainer.addView(more)
        }
    }

    private fun exportBest() {
        val available = results.filter { it.available }
        if (available.isEmpty()) {
            Toast.makeText(this, "没有可用源", Toast.LENGTH_SHORT).show()
            return
        }
        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "text/plain"
            putExtra(Intent.EXTRA_TITLE, "最优直播源.txt")
        }
        startActivityForResult(intent, FILE_EXPORT_CODE)
    }

    private fun exportResults(uri: Uri) {
        scope.launch {
            try {
                val available = results.filter { it.available }
                val content = available.joinToString("\n") { it.url }
                contentResolver.openOutputStream(uri)?.use { os ->
                    os.write(content.toByteArray())
                }
                Toast.makeText(this@MainActivity, "已导出 ${available.size} 个源", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "导出失败: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun dpToPx(dp: Int): Int =
        (dp * resources.displayMetrics.density).toInt()

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}

data class SpeedTestResult(
    val url: String,
    val available: Boolean,
    val latency: Long,
    val statusCode: Int = 0,
    val error: String? = null
)