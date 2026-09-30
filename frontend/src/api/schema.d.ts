export interface paths {
  "/api/products/from-url": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** From Url */
    post: operations["from_url_api_products_from_url_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Products */
    get: operations["products_api_products_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Product */
    get: operations["product_api_products__product_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/raw": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Raw */
    get: operations["raw_api_products__product_id__raw_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/quote": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Quote */
    get: operations["quote_api_products__product_id__quote_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/assets": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Assets */
    get: operations["assets_api_products__product_id__assets_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/listings": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Listings */
    get: operations["listings_api_products__product_id__listings_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/generate": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Generate */
    post: operations["generate_api_products__product_id__generate_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/products/{product_id}/generation-plan": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Plan */
    post: operations["plan_api_products__product_id__generation_plan_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/jobs/{job_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Job */
    get: operations["job_api_jobs__job_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/listings/{listing_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    /** Update */
    patch: operations["update_api_listings__listing_id__patch"];
    trace?: never;
  };
  "/api/listings/{listing_id}/confirm": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Confirm */
    post: operations["confirm_api_listings__listing_id__confirm_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/settings": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Settings */
    get: operations["settings_api_settings_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    /** Patch */
    patch: operations["patch_api_settings_patch"];
    trace?: never;
  };
  "/api/ai-calls": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Calls */
    get: operations["calls_api_ai_calls_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/ai-calls/{call_id}/resolve": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Resolve */
    post: operations["resolve_api_ai_calls__call_id__resolve_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/assets/{asset_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Image */
    get: operations["image_api_assets__asset_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/health": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Health */
    get: operations["health_health_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
}
export type webhooks = Record<string, never>;
export interface components {
  schemas: {
    /** AppStatus */
    AppStatus: {
      /**
       * Source Mode
       * @enum {string}
       */
      source_mode: "live" | "mock";
      /**
       * Ai Mode
       * @enum {string}
       */
      ai_mode: "live" | "mock";
      /** Sources */
      sources: string[];
      /** Domeggook Key Configured */
      domeggook_key_configured: boolean;
      /** Ai Key Configured */
      ai_key_configured: boolean;
      /** Ai Text Model */
      ai_text_model: string;
      /** Ai Image Model */
      ai_image_model: string;
      /**
       * Registration Enabled
       * @default false
       */
      registration_enabled: boolean;
    };
    /** AssetRead */
    AssetRead: {
      /**
       * Id
       * Format: uuid
       */
      id: string;
      /**
       * Product Id
       * Format: uuid
       */
      product_id: string;
      /** Listing Id */
      listing_id: string | null;
      /** Kind */
      kind: string;
      /** Status */
      status: string;
      /** Mode */
      mode: string;
      /** Width */
      width: number | null;
      /** Height */
      height: number | null;
      /** Error */
      error: string | null;
    };
    /** CollectRequest */
    CollectRequest: {
      /** Url */
      url: string;
    };
    /** ConfirmRequest */
    ConfirmRequest: {
      /** Expected Version */
      expected_version: number;
    };
    /** GenerateRequest */
    GenerateRequest: {
      /** Channels */
      channels: ("coupang" | "smartstore")[];
      /**
       * Scope
       * @default all
       * @enum {string}
       */
      scope: "all" | "text" | "thumbnails";
      /**
       * Expected Versions
       * @default {}
       */
      expected_versions: {
        [key: string]: number;
      };
      /**
       * Image Usage Confirmed
       * @default false
       */
      image_usage_confirmed: boolean;
    };
    /** GenerationPlan */
    GenerationPlan: {
      /**
       * Mode
       * @enum {string}
       */
      mode: "live" | "mock";
      /** Text Calls */
      text_calls: number;
      /** Image Calls */
      image_calls: number;
      /** Image Count */
      image_count: number;
      /** Reserved Cost Krw */
      reserved_cost_krw: string;
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components["schemas"]["ValidationError"][];
    };
    /** ImageRef */
    ImageRef: {
      /** Source Url */
      source_url: string;
      /**
       * Role
       * @default source
       */
      role: string;
      /**
       * Sort Order
       * @default 0
       */
      sort_order: number;
    };
    /** Issue */
    Issue: {
      /** Code */
      code: string;
      /** Message */
      message: string;
      /** Field */
      field?: string | null;
      /**
       * Severity
       * @default warning
       * @enum {string}
       */
      severity: "warning" | "error";
    };
    /** JobAccepted */
    JobAccepted: {
      /**
       * Job Id
       * Format: uuid
       */
      job_id: string;
    };
    /** JobRead */
    JobRead: {
      /**
       * Id
       * Format: uuid
       */
      id: string;
      /** Kind */
      kind: string;
      /** Status */
      status: string;
      /** Result */
      result: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      /**
       * Created At
       * Format: date-time
       */
      created_at: string;
      /** Started At */
      started_at: string | null;
      /** Finished At */
      finished_at: string | null;
    };
    JsonValue: unknown;
    /** ListingPatch */
    ListingPatch: {
      /** Expected Version */
      expected_version: number;
      /** Title */
      title?: string | null;
      /** Detail Html */
      detail_html?: string | null;
      /** Selected Thumbnail Id */
      selected_thumbnail_id?: string | null;
      /** Sale Price */
      sale_price?: number | string | null;
      /** Category Code */
      category_code?: string | null;
      /** Options */
      options?: components["schemas"]["JsonValue"][] | null;
      /** Shipping */
      shipping?: {
        [key: string]: components["schemas"]["JsonValue"];
      } | null;
      /** Notices */
      notices?: {
        [key: string]: components["schemas"]["JsonValue"];
      } | null;
      /** Channel Fields */
      channel_fields?: {
        [key: string]: components["schemas"]["JsonValue"];
      } | null;
    };
    /** ListingRead */
    ListingRead: {
      /**
       * Id
       * Format: uuid
       */
      id: string;
      /**
       * Product Id
       * Format: uuid
       */
      product_id: string;
      /**
       * Channel
       * @enum {string}
       */
      channel: "coupang" | "smartstore";
      /**
       * Content Mode
       * @enum {string}
       */
      content_mode: "live" | "mock" | "mixed";
      /** Title */
      title: string | null;
      /** Detail Html */
      detail_html: string | null;
      /** Thumbnail Ids */
      thumbnail_ids: string[];
      /** Selected Thumbnail Id */
      selected_thumbnail_id: string | null;
      /** Sale Price */
      sale_price: string | null;
      /** Currency */
      currency: string | null;
      /** Category Code */
      category_code: string | null;
      /** Options */
      options: components["schemas"]["JsonValue"][];
      /** Shipping */
      shipping: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      /** Notices */
      notices: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      /** Channel Fields */
      channel_fields: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      /**
       * Status
       * @enum {string}
       */
      status: "draft" | "confirmed" | "registered";
      /** Content Version */
      content_version: number;
      /** Confirmed Version */
      confirmed_version: number | null;
      /** Confirmed At */
      confirmed_at: string | null;
      /**
       * Updated At
       * Format: date-time
       */
      updated_at: string;
    };
    /** PriceTier */
    PriceTier: {
      /** Minimum Quantity */
      minimum_quantity: number;
      /** Unit Price */
      unit_price: string;
    };
    /** ProductOption */
    ProductOption: {
      /** Source Option Id */
      source_option_id?: string | null;
      /** Label */
      label?: string | null;
      /** Attributes */
      attributes?: {
        [key: string]: string;
      } | null;
      /** Wholesale Price */
      wholesale_price?: string | null;
      /** Stock Quantity */
      stock_quantity?: number | null;
      /** Available */
      available?: boolean | null;
    };
    /** ProductQuote */
    ProductQuote: {
      /** Quantity */
      quantity: number;
      /** Currency */
      currency: string | null;
      /** Unit Price */
      unit_price?: string | null;
      /** Product Amount */
      product_amount?: string | null;
      /** Shipping Fee */
      shipping_fee?: string | null;
      /** Total Amount */
      total_amount?: string | null;
      /** Issues */
      issues?: components["schemas"]["Issue"][];
    };
    /** ProductRead */
    ProductRead: {
      /** Source */
      source: string;
      /** Source Url */
      source_url: string;
      /**
       * Fetched At
       * Format: date-time
       */
      fetched_at: string;
      /** Source Product Id */
      source_product_id?: string | null;
      /**
       * Acquisition Mode
       * @default live
       * @enum {string}
       */
      acquisition_mode: "live" | "mock";
      /**
       * Collection Status
       * @default partial
       * @enum {string}
       */
      collection_status: "complete" | "partial" | "failed";
      /** Name */
      name?: string | null;
      /** Currency */
      currency?: string | null;
      /** Wholesale Price */
      wholesale_price?: string | null;
      /** Price Tiers */
      price_tiers?: components["schemas"]["PriceTier"][];
      /** Minimum Order Quantity */
      minimum_order_quantity?: number | null;
      /** Purchase Unit */
      purchase_unit?: number | null;
      /** Maximum Order Quantity */
      maximum_order_quantity?: number | null;
      /** Stock Quantity */
      stock_quantity?: number | null;
      /** Options */
      options?: components["schemas"]["ProductOption"][] | null;
      /** Images */
      images?: components["schemas"]["ImageRef"][] | null;
      shipping?: components["schemas"]["Shipping"] | null;
      /** Detail Html */
      detail_html?: string | null;
      /** Detail Text */
      detail_text?: string | null;
      /** Image Usage Allowed */
      image_usage_allowed?: boolean | null;
      /** Raw */
      raw: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      /**
       * Issues
       * @default []
       */
      issues: components["schemas"]["Issue"][];
      /**
       * Id
       * Format: uuid
       */
      id: string;
      /**
       * Created At
       * Format: date-time
       */
      created_at: string;
    };
    /** ResolveCallRequest */
    ResolveCallRequest: {
      /** Actual Cost Krw */
      actual_cost_krw: string;
      /** Evidence */
      evidence: string;
    };
    /** SettingsPatch */
    SettingsPatch: {
      /** Values */
      values: {
        [key: string]: components["schemas"]["JsonValue"];
      };
    };
    /** SettingsRead */
    SettingsRead: {
      /** Values */
      values: {
        [key: string]: components["schemas"]["JsonValue"];
      };
      status: components["schemas"]["AppStatus"];
    };
    /** Shipping */
    Shipping: {
      /** Fee */
      fee?: string | null;
      /** Fee Type */
      fee_type?: string | null;
      /** Fee Table */
      fee_table?: string | null;
      /** Payment Method */
      payment_method?: string | null;
      /**
       * Fee Calculation
       * @default unknown
       * @enum {string}
       */
      fee_calculation: "fixed" | "quantity_tiers" | "unknown";
      /** Quantity Fee Tiers */
      quantity_fee_tiers?: components["schemas"]["PriceTier"][];
      /** Free Shipping Threshold */
      free_shipping_threshold?: string | null;
      /** Remote Area Fee */
      remote_area_fee?: string | null;
      /** Dispatch Days */
      dispatch_days?: number | null;
      /** Origin */
      origin?: string | null;
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
      /** Input */
      input?: unknown;
      /** Context */
      ctx?: Record<string, never>;
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
  from_url_api_products_from_url_post: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["CollectRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["JobAccepted"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  products_api_products_get: {
    parameters: {
      query?: {
        page?: number;
        source?: string | null;
        status?: string | null;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ProductRead"][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  product_api_products__product_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ProductRead"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  raw_api_products__product_id__raw_get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": {
            [key: string]: components["schemas"]["JsonValue"];
          };
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  quote_api_products__product_id__quote_get: {
    parameters: {
      query: {
        quantity: number;
        option_id?: string | null;
      };
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ProductQuote"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  assets_api_products__product_id__assets_get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["AssetRead"][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  listings_api_products__product_id__listings_get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ListingRead"][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  generate_api_products__product_id__generate_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["GenerateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      202: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["JobAccepted"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  plan_api_products__product_id__generation_plan_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        product_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["GenerateRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["GenerationPlan"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  job_api_jobs__job_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        job_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["JobRead"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  update_api_listings__listing_id__patch: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        listing_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["ListingPatch"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ListingRead"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  confirm_api_listings__listing_id__confirm_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        listing_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["ConfirmRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ListingRead"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  settings_api_settings_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["SettingsRead"];
        };
      };
    };
  };
  patch_api_settings_patch: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["SettingsPatch"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["SettingsRead"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  calls_api_ai_calls_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": {
            [key: string]: components["schemas"]["JsonValue"];
          }[];
        };
      };
    };
  };
  resolve_api_ai_calls__call_id__resolve_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        call_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["ResolveCallRequest"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": {
            [key: string]: string;
          };
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  image_api_assets__asset_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        asset_id: string;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": unknown;
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  health_health_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": {
            [key: string]: string;
          };
        };
      };
    };
  };
}
